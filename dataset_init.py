"""Initialize the dashboard database from local CSVs or the public Kaggle source."""
from pathlib import Path
from threading import Lock
from python_eda.validated_etl import TABLES, build

_lock = Lock()
DATASET = "olistbr/brazilian-ecommerce"

def ensure_database(database, downloader=None):
    database = Path(database)
    with _lock:
        if database.is_file():
            return database
        source = database.parent
        if not all((source / name).is_file() for name, _, _ in TABLES.values()):
            if downloader is None:
                import kagglehub
                downloader = kagglehub.dataset_download
            source = Path(downloader(DATASET))
        build(source, database)
        return database
