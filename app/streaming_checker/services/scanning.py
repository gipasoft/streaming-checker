from __future__ import annotations

from streaming_checker.clients.arr_client import ArrItem
from streaming_checker.clients.tmdb_client import TmdbClient
from streaming_checker.core.config import Settings
from streaming_checker.services.provider_normalizer import NormalizedProvider, ProviderNormalizer


def filter_providers(provider_names: list[str], allowlist: list[str]) -> list[str]:
    if not allowlist:
        return provider_names

    allowed = {x.casefold() for x in allowlist}
    return [p for p in provider_names if p.casefold() in allowed]


def filter_normalized_providers(
    providers: list[NormalizedProvider],
    allowlist: list[str],
    normalizer: ProviderNormalizer,
) -> list[NormalizedProvider]:
    if not allowlist:
        return providers

    allowed = {normalizer.canonical_name(value).casefold() for value in allowlist}
    return [provider for provider in providers if provider.canonical_name.casefold() in allowed]


class ScanningService:
    def __init__(self, tmdb: TmdbClient, settings: Settings, normalizer: ProviderNormalizer | None = None):
        self.tmdb = tmdb
        self.settings = settings
        self.normalizer = normalizer or ProviderNormalizer()

    def providers_for_item(self, client_kind: str, item: ArrItem) -> list[str] | None:
        providers = self.normalized_providers_for_item(client_kind, item)
        if providers is None:
            return None
        return ProviderNormalizer.canonical_names(providers)

    def normalized_providers_for_item(self, client_kind: str, item: ArrItem) -> list[NormalizedProvider] | None:
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

        normalized = self.normalizer.normalize_many(providers)
        return filter_normalized_providers(normalized, self.settings.provider_allowlist, self.normalizer)

