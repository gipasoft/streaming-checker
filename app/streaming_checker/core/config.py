import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [x.strip() for x in value.split(",") if x.strip()]


def _float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number") from exc
    if parsed <= 0:
        raise RuntimeError(f"{name} must be greater than zero")
    return parsed


def default_database_path() -> str:
    if Path("/data").is_dir():
        return "/data/streaming_checker.sqlite"
    return "data/streaming_checker.sqlite"


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
    database_path: str

    ntfy_url: str | None
    ntfy_topic: str | None
    ntfy_token: str | None
    ntfy_username: str | None
    ntfy_password: str | None
    ntfy_priority: str
    ntfy_tags: list[str]

    scan_interval_hours: float
    run_scan_on_startup: bool


def load_settings() -> Settings:
    token = os.getenv("TMDB_BEARER_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TMDB_BEARER_TOKEN mancante")
    database_path = os.getenv("DATABASE_PATH", default_database_path()).strip() or default_database_path()
    ntfy_url = os.getenv("NTFY_URL", "").strip().rstrip("/") or None
    ntfy_topic = os.getenv("NTFY_TOPIC", "").strip() or None

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
        database_path=database_path,
        ntfy_url=ntfy_url,
        ntfy_topic=ntfy_topic,
        ntfy_token=os.getenv("NTFY_TOKEN", "").strip() or None,
        ntfy_username=os.getenv("NTFY_USERNAME", "").strip() or None,
        ntfy_password=os.getenv("NTFY_PASSWORD", "").strip() or None,
        ntfy_priority=os.getenv("NTFY_PRIORITY", "default").strip() or "default",
        ntfy_tags=_csv("NTFY_TAGS", "tv"),
        scan_interval_hours=_float("SCAN_INTERVAL_HOURS", 12.0),
        run_scan_on_startup=_bool("RUN_SCAN_ON_STARTUP", True),
    )

