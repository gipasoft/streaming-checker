import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from datetime import UTC, datetime

from streaming_checker.services.runner import ArrScanResult, ScanItemResult, ScanRunResult
from streaming_checker.web.app import (
    _change_status_badge,
    _media_type_badge,
    _providers_display,
    _results_table,
)


class ScanResultsUiTest(unittest.TestCase):
    def test_renders_change_status_badges(self):
        self.assertIn("change-new", _change_status_badge("NEW"))
        self.assertIn("change-updated", _change_status_badge("UPDATED"))
        self.assertIn("change-unchanged", _change_status_badge("UNCHANGED"))
        self.assertIn("change-removed", _change_status_badge("REMOVED"))

    def test_renders_media_type_badges(self):
        self.assertIn("badge-movie", _media_type_badge("movie"))
        self.assertIn("badge-series", _media_type_badge("series"))

    def test_provider_display_uses_chips_and_debug_originals(self):
        html = _providers_display(["Amazon Prime Video"], ["Prime Video"])

        self.assertIn("provider-chip", html)
        self.assertIn("Amazon Prime Video", html)
        self.assertIn("TMDB: Prime Video", html)

    def test_results_table_uses_scroll_wrapper_and_wrapping_message_cell(self):
        now = datetime.now(UTC)
        result = ScanRunResult(
            started_at=now,
            finished_at=now,
            duration_seconds=0.1,
            country="IT",
            dry_run=True,
            offer_types=["flatrate"],
            arr_results=[
                ArrScanResult(
                    kind="radarr",
                    enabled=True,
                    missing_count=1,
                    items=[
                        ScanItemResult(
                            kind="radarr",
                            media_type="movie",
                            title="Movie",
                            status="processed",
                            change_status="UNCHANGED",
                            providers=["Amazon Prime Video"],
                            message="providers changed; added: Amazon Prime Video; removed: -",
                        )
                    ],
                )
            ],
        )

        html = _results_table(result)

        self.assertIn("table-scroll", html)
        self.assertIn("results-table", html)
        self.assertIn("message-cell", html)


if __name__ == "__main__":
    unittest.main()
