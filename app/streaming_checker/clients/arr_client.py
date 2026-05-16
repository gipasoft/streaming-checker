from __future__ import annotations

from dataclasses import dataclass

from streaming_checker.clients.http_client import HttpClient


@dataclass
class ArrItem:
    id: int
    title: str
    tmdb_id: int | None
    tvdb_id: int | None
    tags: list[int]
    raw: dict


class ArrClient:
    def __init__(self, base_url: str, api_key: str, kind: str):
        self.kind = kind
        self.http = HttpClient(
            base_url,
            headers={"X-Api-Key": api_key},
        )
        self._tag_cache: dict[str, int] | None = None

    def get_tags(self) -> dict[str, int]:
        if self._tag_cache is None:
            tags = self.http.get("/api/v3/tag") or []
            self._tag_cache = {t["label"]: t["id"] for t in tags}
        return self._tag_cache

    def ensure_tag(self, label: str, dry_run: bool) -> int | None:
        tags = self.get_tags()
        if label in tags:
            return tags[label]

        if dry_run:
            print(f"[{self.kind}] DRY-RUN create tag: {label}")
            return None

        created = self.http.post("/api/v3/tag", json={"label": label})
        tag_id = int(created["id"])
        self._tag_cache = None
        return tag_id

    def managed_tag_ids(self, generic_tag: str, tag_prefix: str) -> set[int]:
        tags = self.get_tags()
        return {
            tag_id
            for label, tag_id in tags.items()
            if label == generic_tag or label.startswith(tag_prefix)
        }

    def list_missing_monitored(self) -> list[ArrItem]:
        if self.kind == "radarr":
            return self._list_radarr_missing()
        if self.kind == "sonarr":
            return self._list_sonarr_missing()
        raise ValueError(f"Unsupported kind: {self.kind}")

    def _list_radarr_missing(self) -> list[ArrItem]:
        movies = self.http.get("/api/v3/movie") or []
        result: list[ArrItem] = []

        for movie in movies:
            if not movie.get("monitored"):
                continue

            # In Radarr, a missing/null movieFile usually means the movie is missing.
            if movie.get("movieFile"):
                continue

            result.append(
                ArrItem(
                    id=int(movie["id"]),
                    title=movie.get("title", f"movie-{movie['id']}"),
                    tmdb_id=movie.get("tmdbId"),
                    tvdb_id=None,
                    tags=list(movie.get("tags") or []),
                    raw=movie,
                )
            )

        return result

    def _list_sonarr_missing(self) -> list[ArrItem]:
        series_list = self.http.get("/api/v3/series") or []
        result: list[ArrItem] = []

        for series in series_list:
            if not series.get("monitored"):
                continue

            stats = series.get("statistics") or {}
            episode_count = int(stats.get("episodeCount") or 0)
            episode_file_count = int(stats.get("episodeFileCount") or 0)

            if episode_count > 0 and episode_file_count >= episode_count:
                continue

            result.append(
                ArrItem(
                    id=int(series["id"]),
                    title=series.get("title", f"series-{series['id']}"),
                    tmdb_id=series.get("tmdbId"),
                    tvdb_id=series.get("tvdbId"),
                    tags=list(series.get("tags") or []),
                    raw=series,
                )
            )

        return result

    def update_tags(
        self,
        item: ArrItem,
        desired_tag_labels: set[str],
        *,
        generic_tag: str,
        tag_prefix: str,
        remove_stale: bool,
        dry_run: bool,
    ):
        current_ids = set(item.tags)
        desired_ids: set[int] = set()

        for label in sorted(desired_tag_labels):
            tag_id = self.ensure_tag(label, dry_run=dry_run)
            if tag_id is not None:
                desired_ids.add(tag_id)

        managed_ids = self.managed_tag_ids(generic_tag, tag_prefix) if remove_stale else set()
        new_ids = set(current_ids)

        if remove_stale:
            new_ids -= managed_ids

        new_ids |= desired_ids

        if new_ids == current_ids:
            print(f"[{self.kind}] unchanged: {item.title}")
            return

        current_labels = self._labels_for_ids(current_ids)
        new_labels = self._labels_for_ids(new_ids)
        print(f"[{self.kind}] update tags: {item.title}")
        print(f"  current: {sorted(current_labels)}")
        print(f"  new:     {sorted(new_labels)}")

        if dry_run:
            return

        updated = dict(item.raw)
        updated["tags"] = sorted(new_ids)

        if self.kind == "radarr":
            self.http.put(f"/api/v3/movie/{item.id}", json=updated)
        else:
            self.http.put(f"/api/v3/series/{item.id}", json=updated)

    def _labels_for_ids(self, ids: set[int]) -> list[str]:
        tags = self.get_tags()
        reverse = {tag_id: label for label, tag_id in tags.items()}
        return [reverse.get(i, f"#{i}") for i in ids]

