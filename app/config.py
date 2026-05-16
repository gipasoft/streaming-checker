import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    radarr_url: str | None
    radarr_api_key: str | None
    sonarr_url: str | None
    sonarr_api_key: str | None

    tmdb_bearer_token: str
    country: str
    language: str

    dry_run: bool
    remove_stale_tags: bool
    tag_generic: bool
    tag_providers: bool
    generic_tag: str
    tag_prefix: str

    provider_allowlist: list[str]
    offer_types: list[str]


def load_settings() -> Settings:
    token = os.getenv("TMDB_BEARER_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TMDB_BEARER_TOKEN mancante")

    return Settings(
        radarr_url=os.getenv("RADARR_URL", "").rstrip("/") or None,
        radarr_api_key=os.getenv("RADARR_API_KEY", "").strip() or None,
        sonarr_url=os.getenv("SONARR_URL", "").rstrip("/") or None,
        sonarr_api_key=os.getenv("SONARR_API_KEY", "").strip() or None,
        tmdb_bearer_token=token,
        country=os.getenv("COUNTRY", "IT").strip().upper(),
        language=os.getenv("LANGUAGE", "it-IT").strip(),
        dry_run=_bool("DRY_RUN", True),
        remove_stale_tags=_bool("REMOVE_STALE_TAGS", True),
        tag_generic=_bool("TAG_GENERIC", True),
        tag_providers=_bool("TAG_PROVIDERS", True),
        generic_tag=os.getenv("GENERIC_TAG", "available-streaming").strip(),
        tag_prefix=os.getenv("TAG_PREFIX", "streaming-").strip(),
        provider_allowlist=_csv("PROVIDER_ALLOWLIST"),
        offer_types=_csv("OFFER_TYPES", "flatrate,free,ads"),
    )
