import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from streaming_checker.web.app import _change_status_badge, _media_type_badge, _providers_display


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


if __name__ == "__main__":
    unittest.main()
