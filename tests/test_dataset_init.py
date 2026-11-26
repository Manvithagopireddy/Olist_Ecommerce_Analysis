import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from dataset_init import ensure_database, DATASET
from python_eda.validated_etl import TABLES

class TestInitialization(unittest.TestCase):
    def test_existing_database_does_not_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "olist.db"
            db.touch()
            download = Mock()
            self.assertEqual(ensure_database(db, download), db)
            download.assert_not_called()

    def test_local_csvs_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, _, _ in TABLES.values():
                (root / name).touch()
            download = Mock()
            with patch("dataset_init.build") as build:
                ensure_database(root / "olist.db", download)
                build.assert_called_once_with(root, root / "olist.db")
            download.assert_not_called()

    def test_missing_data_downloads_and_builds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            download = Mock(return_value=str(root / "download"))
            with patch("dataset_init.build") as build:
                ensure_database(root / "data" / "olist.db", download)
                build.assert_called_once_with(root / "download", root / "data" / "olist.db")
            download.assert_called_once_with(DATASET)

    def test_download_failure_propagates(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "olist.db"
            with self.assertRaises(RuntimeError):
                ensure_database(db, Mock(side_effect=RuntimeError("offline")))
            self.assertFalse(db.exists())
