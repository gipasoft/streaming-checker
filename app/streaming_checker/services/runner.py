from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import perf_counter
from typing import Callable

from streaming_checker.clients.arr_client import ArrClient, ArrItem
from streaming_checker.clients.tmdb_client import TmdbClient
from streaming_checker.core.config import Settings
from streaming_checker.services.scanning import ScanningService
from streaming_checker.services.tagging import TaggingService


@dataclass(frozen=True)
class ScanItemResult:
    kind: str
    title: str
    status: str
    providers: list[str] = field(default_factory=list)
    message: str | None = None


@dataclass(frozen=True)
class ArrScanResult:
    kind: str
    enabled: bool
    missing_count: int = 0
    items: list[ScanItemResult] = field(default_factory=list)
    message: str | None = None

    @property
    def processed_count(self) -> int:
        return sum(1 for item in self.items if item.status == "processed")

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.items if item.status == "skipped")

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.items if item.status == "error")


@dataclass(frozen=True)
class ScanRunResult:
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    country: str
    dry_run: bool
    offer_types: list[str]
    arr_results: list[ArrScanResult]

    @property
    def missing_count(self) -> int:
        return sum(result.missing_count for result in self.arr_results)

    @property
    def processed_count(self) -> int:
        return sum(result.processed_count for result in self.arr_results)

    @property
    def skipped_count(self) -> int:
        return sum(result.skipped_count for result in self.arr_results)

    @property
    def error_count(self) -> int:
        return sum(result.error_count for result in self.arr_results)


class ScanRunner:
    def __init__(
        self,
        settings: Settings,
        *,
        tmdb_factory: Callable[[str, str], TmdbClient] = TmdbClient,
        arr_client_factory: Callable[[str, str, str], ArrClient] = ArrClient,
    ):
        self.settings = settings
        self.tmdb_factory = tmdb_factory
        self.arr_client_factory = arr_client_factory

    def run(self) -> ScanRunResult:
        started_at = datetime.now(UTC)
        start = perf_counter()
        tmdb = self.tmdb_factory(self.settings.tmdb_bearer_token, self.settings.language)
        arr_results: list[ArrScanResult] = []

        if self.settings.radarr_url and self.settings.radarr_api_key:
            arr_results.append(
                self.process_arr(
                    self.arr_client_factory(self.settings.radarr_url, self.settings.radarr_api_key, "radarr"),
                    tmdb,
                )
            )
        else:
            print("[radarr] disabled")
            arr_results.append(ArrScanResult(kind="radarr", enabled=False, message="disabled"))

        if self.settings.sonarr_url and self.settings.sonarr_api_key:
            arr_results.append(
                self.process_arr(
                    self.arr_client_factory(self.settings.sonarr_url, self.settings.sonarr_api_key, "sonarr"),
                    tmdb,
                )
            )
        else:
            print("[sonarr] disabled")
            arr_results.append(ArrScanResult(kind="sonarr", enabled=False, message="disabled"))

        finished_at = datetime.now(UTC)
        return ScanRunResult(
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=perf_counter() - start,
            country=self.settings.country,
            dry_run=self.settings.dry_run,
            offer_types=list(self.settings.offer_types),
            arr_results=arr_results,
        )

    def process_arr(self, client: ArrClient, tmdb: TmdbClient) -> ArrScanResult:
        items = client.list_missing_monitored()
        print(f"[{client.kind}] missing monitored items: {len(items)}")

        scanner = ScanningService(tmdb, self.settings)
        tagger = TaggingService(self.settings)
        item_results: list[ScanItemResult] = []

        for item in items:
            item_results.append(self._process_item(client, scanner, tagger, item))

        return ArrScanResult(
            kind=client.kind,
            enabled=True,
            missing_count=len(items),
            items=item_results,
        )

    def _process_item(
        self,
        client: ArrClient,
        scanner: ScanningService,
        tagger: TaggingService,
        item: ArrItem,
    ) -> ScanItemResult:
        try:
            providers = scanner.providers_for_item(client.kind, item)
            if providers is None:
                return ScanItemResult(
                    kind=client.kind,
                    title=item.title,
                    status="skipped",
                    message="missing tmdbId/tvdbId mapping",
                )

            tagger.apply(client, item, providers)
            return ScanItemResult(
                kind=client.kind,
                title=item.title,
                status="processed",
                providers=providers,
            )
        except Exception as exc:
            print(f"[{client.kind}] ERROR processing {item.title}: {exc}")
            return ScanItemResult(
                kind=client.kind,
                title=item.title,
                status="error",
                message=str(exc),
            )

