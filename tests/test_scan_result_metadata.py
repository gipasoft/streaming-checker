import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from watcharr.clients.arr_client import ArrItem
from watcharr.core.config import Settings
from watcharr.services.runner import ScanRunner


class ScanResultMetadataTest(unittest.TestCase):
    def test_arr_detail_urls_use_internal_arr_ids(self):
        runner = _runner()

        self.assertEqual(runner._arr_detail_url("radarr", 123), "https://radarr.local/movie/123")
        self.assertEqual(runner._arr_detail_url("sonarr", 456), "https://sonarr.local/series/456")

    def test_poster_url_prefers_tmdb_metadata_from_arr_images(self):
        runner = _runner()
        item = ArrItem(
            id=123,
            title="Movie",
            tmdb_id=999,
            tvdb_id=None,
            tags=[],
            raw={
                "images": [
                    {"coverType": "poster", "url": "/MediaCover/123/poster.jpg"},
                    {"coverType": "poster", "remoteUrl": "https://image.tmdb.org/t/p/original/movie.jpg"},
                ]
            },
        )

        self.assertEqual(runner._poster_url("radarr", item), "https://image.tmdb.org/t/p/w92/movie.jpg")

    def test_poster_path_uses_compact_tmdb_size(self):
        runner = _runner()
        item = ArrItem(
            id=456,
            title="Series",
            tmdb_id=111,
            tvdb_id=222,
            tags=[],
            raw={"poster_path": "/series.jpg"},
        )

        self.assertEqual(runner._poster_url("sonarr", item), "https://image.tmdb.org/t/p/w92/series.jpg")


def _runner() -> ScanRunner:
    return ScanRunner(_settings(), storage_factory=None, notifier_factory=None)


def _settings() -> Settings:
    return Settings(
        radarr_url="https://radarr.local",
        radarr_api_key="radarr",
        sonarr_url="https://sonarr.local",
        sonarr_api_key="sonarr",
        tmdb_bearer_token="tmdb",
        country="IT",
        language="it-IT",
        dry_run=True,
        remove_stale_tags=True,
        tag_generic=True,
        tag_providers=True,
        generic_tag="available-streaming",
        tag_prefix="streaming-",
        provider_allowlist=[],
        offer_types=["flatrate"],
        database_path=":memory:",
        ntfy_url=None,
        ntfy_topic=None,
        ntfy_token=None,
        ntfy_username=None,
        ntfy_password=None,
        ntfy_priority="default",
        ntfy_tags=[],
        scan_interval_hours=12.0,
        run_scan_on_startup=True,
    )


if __name__ == "__main__":
    unittest.main()
