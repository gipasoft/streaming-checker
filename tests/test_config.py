import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from watcharr.core.config import load_settings


class ConfigTest(unittest.TestCase):
    def test_loads_scheduler_settings_from_environment(self):
        env = {
            "TMDB_BEARER_TOKEN": "tmdb",
            "SCAN_INTERVAL_HOURS": "6",
            "RUN_SCAN_ON_STARTUP": "false",
        }

        with patch.dict(os.environ, env, clear=True):
            settings = load_settings()

        self.assertEqual(settings.scan_interval_hours, 6.0)
        self.assertFalse(settings.run_scan_on_startup)


if __name__ == "__main__":
    unittest.main()

