from __future__ import annotations

from watcharr.clients.arr_client import ArrClient
from watcharr.clients.tmdb_client import TmdbClient
from watcharr.core.config import Settings, load_settings
from watcharr.services.runner import ArrScanResult, ScanRunner


def process_arr(client: ArrClient, tmdb: TmdbClient, settings: Settings) -> ArrScanResult:
    return ScanRunner(settings).process_arr(client, tmdb)


def main():
    settings = load_settings()
    print("watcharr started")
    print(f"country={settings.country} dry_run={settings.dry_run} offer_types={settings.offer_types}")

    ScanRunner(settings).run()


if __name__ == "__main__":
    main()
