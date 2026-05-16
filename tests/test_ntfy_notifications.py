import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from streaming_checker.core.config import Settings
from streaming_checker.services.notifications import NtfyNotifier
from streaming_checker.storage.sqlite import AvailabilityChange


def make_settings(**overrides):
    values = {
        "radarr_url": None,
        "radarr_api_key": None,
        "sonarr_url": None,
        "sonarr_api_key": None,
        "tmdb_bearer_token": "tmdb",
        "country": "IT",
        "language": "it-IT",
        "dry_run": True,
        "remove_stale_tags": True,
        "tag_generic": True,
        "tag_providers": True,
        "generic_tag": "available-streaming",
        "tag_prefix": "streaming-",
        "provider_allowlist": [],
        "offer_types": ["flatrate"],
        "database_path": ":memory:",
        "ntfy_url": "https://ntfy.example.com",
        "ntfy_topic": "streaming",
        "ntfy_token": "token",
        "ntfy_username": None,
        "ntfy_password": None,
        "ntfy_priority": "high",
        "ntfy_tags": ["tv", "streaming"],
        "scan_interval_hours": 12.0,
        "run_scan_on_startup": True,
    }
    values.update(overrides)
    return Settings(**values)


class NtfyNotifierTest(unittest.TestCase):
    def test_builds_concise_provider_change_message(self):
        notifier = NtfyNotifier(make_settings())
        change = AvailabilityChange(
            media_key="radarr:1",
            previous_known=True,
            previous_providers=["Netflix"],
            current_providers=["Netflix", "Prime Video"],
            added_providers=["Prime Video"],
            removed_providers=[],
            changed=True,
            notification_created=True,
        )

        message = notifier.build_provider_change_message(kind="radarr", title="Movie", change=change)

        self.assertEqual(message.title, "Provider streaming cambiati")
        self.assertEqual(message.priority, "high")
        self.assertEqual(message.tags, ["tv", "streaming"])
        self.assertIn("Movie (radarr)", message.body)
        self.assertIn("Aggiunti: Prime Video", message.body)
        self.assertIn("Rimossi: -", message.body)

    @patch("streaming_checker.services.notifications.requests.post")
    def test_sends_to_self_hosted_server_with_headers(self, post):
        post.return_value.raise_for_status.return_value = None
        notifier = NtfyNotifier(make_settings(ntfy_url="https://ntfy.internal", ntfy_topic="media alerts"))
        change = AvailabilityChange(
            media_key="sonarr:2",
            previous_known=True,
            current_providers=["Disney+"],
            added_providers=["Disney+"],
            changed=True,
            notification_created=True,
        )

        sent = notifier.notify_provider_change(kind="sonarr", title="Series", change=change)

        self.assertTrue(sent)
        post.assert_called_once()
        url = post.call_args.args[0]
        kwargs = post.call_args.kwargs
        self.assertEqual(url, "https://ntfy.internal/media%20alerts")
        self.assertEqual(kwargs["headers"]["Priority"], "high")
        self.assertEqual(kwargs["headers"]["Tags"], "tv,streaming")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")
        self.assertIn("Series (sonarr)", kwargs["data"].decode("utf-8"))

    def test_disabled_without_url_or_topic(self):
        self.assertFalse(NtfyNotifier(make_settings(ntfy_url=None)).enabled)
        self.assertFalse(NtfyNotifier(make_settings(ntfy_topic=None)).enabled)


if __name__ == "__main__":
    unittest.main()
