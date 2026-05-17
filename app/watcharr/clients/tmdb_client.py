from __future__ import annotations

from watcharr.clients.http_client import HttpClient


class TmdbClient:
    def __init__(self, bearer_token: str, language: str):
        self.language = language
        self.http = HttpClient(
            "https://api.themoviedb.org/3",
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Accept": "application/json",
            },
        )

    def movie_providers(self, tmdb_id: int, country: str, offer_types: list[str]) -> list[str]:
        data = self.http.get(f"/movie/{tmdb_id}/watch/providers") or {}
        return self._extract_providers(data, country, offer_types)

    def tv_providers(self, tmdb_id: int, country: str, offer_types: list[str]) -> list[str]:
        data = self.http.get(f"/tv/{tmdb_id}/watch/providers") or {}
        return self._extract_providers(data, country, offer_types)

    def tmdb_tv_id_from_tvdb(self, tvdb_id: int) -> int | None:
        data = self.http.get(
            f"/find/{tvdb_id}",
            params={"external_source": "tvdb_id", "language": self.language},
        ) or {}

        results = data.get("tv_results") or []
        if not results:
            return None

        return int(results[0]["id"])

    @staticmethod
    def _extract_providers(data: dict, country: str, offer_types: list[str]) -> list[str]:
        country_data = (data.get("results") or {}).get(country.upper()) or {}
        names: set[str] = set()

        for offer_type in offer_types:
            for provider in country_data.get(offer_type, []) or []:
                name = provider.get("provider_name")
                if name:
                    names.add(name)

        return sorted(names)

