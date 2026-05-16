from __future__ import annotations

from streaming_checker.clients.arr_client import ArrItem
from streaming_checker.clients.tmdb_client import TmdbClient
from streaming_checker.core.config import Settings


def filter_providers(provider_names: list[str], allowlist: list[str]) -> list[str]:
    if not allowlist:
        return provider_names

    allowed = {x.casefold() for x in allowlist}
    return [p for p in provider_names if p.casefold() in allowed]


class ScanningService:
    def __init__(self, tmdb: TmdbClient, settings: Settings):
        self.tmdb = tmdb
        self.settings = settings

    def providers_for_item(self, client_kind: str, item: ArrItem) -> list[str] | None:
        if client_kind == "radarr":
            if not item.tmdb_id:
                print(f"[radarr] skip without tmdbId: {item.title}")
                return None
            providers = self.tmdb.movie_providers(item.tmdb_id, self.settings.country, self.settings.offer_types)
        else:
            tmdb_id = item.tmdb_id
            if not tmdb_id and item.tvdb_id:
                tmdb_id = self.tmdb.tmdb_tv_id_from_tvdb(item.tvdb_id)

            if not tmdb_id:
                print(f"[sonarr] skip without tmdbId/tvdbId mapping: {item.title}")
                return None

            providers = self.tmdb.tv_providers(tmdb_id, self.settings.country, self.settings.offer_types)

        return filter_providers(providers, self.settings.provider_allowlist)

