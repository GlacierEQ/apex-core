"""
APEX RCLONE ORCHESTRATOR L2 UNIT TESTS
Standard: Verifies multi-cloud horizon detection, mock syncing, and status telemetry.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

import sys
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from apex_rclone_orchestrator import ApexRcloneOrchestrator


class TestApexRcloneOrchestrator(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="apex_rclone_test_"))
        self.orchestrator = ApexRcloneOrchestrator()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_rclone_binary_detection(self):
        """Verifies that the system Rclone binary is detected and executable."""
        self.assertTrue(self.orchestrator.is_rclone_available(), "Rclone binary must be available on host")

    def test_02_configured_remotes_parsing(self):
        """Verifies configured remotes includes gdrive."""
        remotes = self.orchestrator.get_configured_remotes()
        self.assertIsInstance(remotes, list)
        self.assertIn("gdrive:", remotes)

    def test_03_inspect_horizon_status_structure(self):
        """Verifies status schema contains all three horizons."""
        stat = self.orchestrator.inspect_horizon_status()
        self.assertIn("timestamp_utc", stat)
        self.assertIn("horizons", stat)
        self.assertIn("local_apex", stat["horizons"])
        self.assertIn("shadowdrive", stat["horizons"])
        self.assertIn("gdrive", stat["horizons"])

    def test_04_local_dry_run_sync(self):
        """Verifies that a local dry-run sync completes with success code."""
        src = self.test_dir / "src"
        src.mkdir()
        (src / "test.txt").write_text("APEX Rclone Test Payload", encoding="utf-8")

        dst = self.test_dir / "dst"
        dst.mkdir()

        res = self.orchestrator.sync_path(str(src), str(dst), dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["exit_code"], 0)
        self.assertTrue(res["dry_run"])


if __name__ == "__main__":
    unittest.main()
