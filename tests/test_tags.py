import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from watcharr.core.tags import desired_tags, provider_tag, slug_provider


class TagGenerationTest(unittest.TestCase):
    def test_slug_provider_normalizes_streaming_names(self):
        self.assertEqual(slug_provider(" Prime Video "), "prime-video")
        self.assertEqual(slug_provider("Disney+"), "disney")
        self.assertEqual(slug_provider("MUBI & More"), "mubi-and-more")

    def test_provider_tag_uses_configured_prefix(self):
        self.assertEqual(provider_tag("streaming-", "Prime Video"), "streaming-prime-video")

    def test_desired_tags_includes_generic_and_provider_tags(self):
        self.assertEqual(
            desired_tags(
                ["Netflix", "Prime Video"],
                tag_generic=True,
                tag_providers=True,
                generic_tag="available-streaming",
                tag_prefix="streaming-",
            ),
            {"available-streaming", "streaming-netflix", "streaming-prime-video"},
        )

    def test_desired_tags_without_providers_is_empty(self):
        self.assertEqual(
            desired_tags(
                [],
                tag_generic=True,
                tag_providers=True,
                generic_tag="available-streaming",
                tag_prefix="streaming-",
            ),
            set(),
        )


if __name__ == "__main__":
    unittest.main()
