import os
from pathlib import Path
import sqlite3
import tempfile
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Ensure tests have a working database for v2 endpoints and select_query:
# 1. Use existing EPICSA_SQLITE_DB if already set and valid
# 2. Check for local snapshot: data_snapshot/epicsa_local.db
# 3. Fall back to creating a temporary SQLite db from app/tests/data/test_epicsa.sql
if not os.environ.get("EPICSA_SQLITE_DB") or not Path(os.environ["EPICSA_SQLITE_DB"]).exists():
    snapshot_db = Path("data_snapshot/epicsa_local.db").resolve()
    sql_fixture = Path(__file__).parent / "tests" / "data" / "test_epicsa.sql"
    if snapshot_db.exists():
        os.environ["EPICSA_SQLITE_DB"] = str(snapshot_db)
    elif sql_fixture.exists():
        tmp_db = Path(tempfile.gettempdir()) / "epicsa_test_fixture.db"
        if not tmp_db.exists() or tmp_db.stat().st_size == 0:
            conn = sqlite3.connect(tmp_db)
            conn.executescript(sql_fixture.read_text(encoding="utf-8"))
            conn.close()
        os.environ["EPICSA_SQLITE_DB"] = str(tmp_db)

from .test_main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
