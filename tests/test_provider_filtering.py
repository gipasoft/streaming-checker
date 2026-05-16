import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from streaming_checker.services.scanning import filter_providers


class ProviderFilteringTest(unittest.TestCase):
    def test_empty_allowlist_keeps_all_providers_in_original_order(self):
        self.assertEqual(filter_providers(["Netflix", "Prime Video"], []), ["Netflix", "Prime Video"])

    def test_allowlist_matches_case_insensitively(self):
        self.assertEqual(
            filter_providers(["Netflix", "Prime Video", "Disney+"], ["netflix", "DISNEY+"]),
            ["Netflix", "Disney+"],
        )

    def test_allowlist_does_not_partial_match(self):
        self.assertEqual(filter_providers(["Amazon Prime Video"], ["Prime Video"]), [])


if __name__ == "__main__":
    unittest.main()
