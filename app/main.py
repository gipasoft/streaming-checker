from __future__ import annotations

from arr_client import ArrClient
from config import Settings, load_settings
from tags import desired_tags
from tmdb_client import TmdbClient


def filter_providers(provider_names: list[str], allowlist: list[str]) -> list[str]:
    if not allowlist:
        return provider_names

    allowed = {x.casefold() for x in allowlist}
    return [p for p in provider_names if p.casefold() in allowed]


def process_arr(client: ArrClient, tmdb: TmdbClient, settings: Settings):
    items = client.list_missing_monitored()
    print(f"[{client.kind}] missing monitored items: {len(items)}")

    for item in items:
        try:
            if client.kind == "radarr":
                if not item.tmdb_id:
                    print(f"[radarr] skip without tmdbId: {item.title}")
                    continue
                providers = tmdb.movie_providers(item.tmdb_id, settings.country, settings.offer_types)
            else:
                tmdb_id = item.tmdb_id
                if not tmdb_id and item.tvdb_id:
                    tmdb_id = tmdb.tmdb_tv_id_from_tvdb(item.tvdb_id)

                if not tmdb_id:
                    print(f"[sonarr] skip without tmdbId/tvdbId mapping: {item.title}")
                    continue

                providers = tmdb.tv_providers(tmdb_id, settings.country, settings.offer_types)

            providers = filter_providers(providers, settings.provider_allowlist)
            labels = desired_tags(
                providers,
                tag_generic=settings.tag_generic,
                tag_providers=settings.tag_providers,
                generic_tag=settings.generic_tag,
                tag_prefix=settings.tag_prefix,
            )

            if providers:
                print(f"[{client.kind}] {item.title}: {', '.join(providers)}")
            else:
                print(f"[{client.kind}] {item.title}: no providers")

            client.update_tags(
                item,
                labels,
                generic_tag=settings.generic_tag,
                tag_prefix=settings.tag_prefix,
                remove_stale=settings.remove_stale_tags,
                dry_run=settings.dry_run,
            )

        except Exception as exc:
            print(f"[{client.kind}] ERROR processing {item.title}: {exc}")


def main():
    settings = load_settings()
    print("streaming-checker started")
    print(f"country={settings.country} dry_run={settings.dry_run} offer_types={settings.offer_types}")

    tmdb = TmdbClient(settings.tmdb_bearer_token, settings.language)

    if settings.radarr_url and settings.radarr_api_key:
        process_arr(ArrClient(settings.radarr_url, settings.radarr_api_key, "radarr"), tmdb, settings)
    else:
        print("[radarr] disabled")

    if settings.sonarr_url and settings.sonarr_api_key:
        process_arr(ArrClient(settings.sonarr_url, settings.sonarr_api_key, "sonarr"), tmdb, settings)
    else:
        print("[sonarr] disabled")


if __name__ == "__main__":
    main()
