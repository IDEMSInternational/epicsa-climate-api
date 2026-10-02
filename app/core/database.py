import atexit
from functools import lru_cache
import json
import os
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from app.core.config import Settings

try:
    import psycopg
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool, PoolTimeout
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None
    ConnectionPool = None
    PoolTimeout = None

_STATEMENT_TIMEOUT_MS = 5000
_POOL_LOCK = Lock()
_CONNECTION_POOL: Optional[Any] = None
_CONNECTION_POOL_KEY: Optional[Tuple[Any, ...]] = None


@lru_cache(maxsize=8)
def _read_and_parse_secret_file(path_str: str, mtime: float) -> Dict[str, Any]:
    path = Path(path_str)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Postgres secret file is not valid JSON: {error}",
        ) from error


def load_db_secret(secret_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Load and validate PostgreSQL credentials from JSON file."""
    path_to_use = secret_file_path or Settings().POSTGRES_SECRET_FILE
    secret_path = Path(path_to_use)

    if not secret_path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Postgres secret file not found at '{secret_path}'. "
                "Set POSTGRES_SECRET_FILE to a valid file path."
            ),
        )

    mtime = secret_path.stat().st_mtime
    secret = _read_and_parse_secret_file(str(secret_path.resolve()), mtime)

    required_keys = ["host", "port", "dbname", "user", "password"]
    missing_keys = [key for key in required_keys if key not in secret]
    if missing_keys:
        raise HTTPException(
            status_code=500,
            detail=f"Postgres secret file missing required keys: {', '.join(missing_keys)}",
        )

    return secret


def _pool_key_from_secret(secret: Dict[str, Any]) -> Tuple[Any, ...]:
    return (
        secret["host"],
        secret["port"],
        secret["dbname"],
        secret["user"],
        secret["password"],
        secret.get("sslmode", "prefer"),
    )


def get_connection_pool(secret: Optional[Dict[str, Any]] = None):
    """Retrieve or initialize the thread-safe PostgreSQL connection pool."""
    global _CONNECTION_POOL, _CONNECTION_POOL_KEY

    if ConnectionPool is None:
        raise RuntimeError("psycopg-pool is not installed. Add psycopg-pool to dependencies.")

    if secret is None:
        secret = load_db_secret()

    pool_key = _pool_key_from_secret(secret)
    with _POOL_LOCK:
        if _CONNECTION_POOL is not None and _CONNECTION_POOL_KEY != pool_key:
            _CONNECTION_POOL.close()
            _CONNECTION_POOL = None
            _CONNECTION_POOL_KEY = None

        if _CONNECTION_POOL is None:
            settings = Settings()
            conn_kwargs = {
                "host": secret["host"],
                "port": secret.get("port", 5432),
                "dbname": secret["dbname"],
                "user": secret["user"],
                "password": secret["password"],
                "sslmode": secret.get("sslmode", "prefer"),
                "connect_timeout": 10,
            }
            _CONNECTION_POOL = ConnectionPool(
                kwargs=conn_kwargs,
                min_size=settings.POSTGRES_POOL_MIN_CONNECTIONS,
                max_size=settings.POSTGRES_POOL_MAX_CONNECTIONS,
                timeout=settings.POSTGRES_POOL_TIMEOUT_SECONDS,
                check=ConnectionPool.check_connection,
                max_idle=300.0,
                open=True,
            )
            _CONNECTION_POOL_KEY = pool_key

        return _CONNECTION_POOL


def close_connection_pool() -> None:
    """Close all open connections in the pool on application shutdown."""
    global _CONNECTION_POOL, _CONNECTION_POOL_KEY

    with _POOL_LOCK:
        if _CONNECTION_POOL is not None:
            _CONNECTION_POOL.close()
            _CONNECTION_POOL = None
            _CONNECTION_POOL_KEY = None


atexit.register(close_connection_pool)


def execute_query(
    sql: str,
    params: Optional[List[Any] | Tuple[Any, ...]] = None,
    secret: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Execute a parameterized SQL query in a read-only transaction.
    Returns (column_names, rows_as_dicts).
    """
    if params is None:
        params = []

    # Optional local SQLite mode for offline testing / development
    sqlite_db = os.environ.get("EPICSA_SQLITE_DB")
    if sqlite_db and Path(sqlite_db).exists():
        return _execute_sqlite_query(sqlite_db, sql, params)

    if psycopg is None or ConnectionPool is None:
        raise RuntimeError("psycopg is not installed. Add psycopg[binary] and psycopg-pool to requirements.")

    pool = get_connection_pool(secret)
    with pool.connection() as connection:
        connection.read_only = True
        connection.autocommit = False
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(f"SET LOCAL statement_timeout = {int(_STATEMENT_TIMEOUT_MS)}")
            cursor.execute(sql, tuple(params))
            rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
            columns = [column.name for column in cursor.description] if cursor.description else []
            connection.rollback()
            return columns, rows


def _execute_sqlite_query(
    sqlite_path: str,
    sql: str,
    params: List[Any] | Tuple[Any, ...],
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Execute against local SQLite for offline testing."""
    # Convert %s placeholders to ? placeholders for sqlite
    sqlite_sql = sql.replace("%s", "?")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(sqlite_sql, tuple(params))
        rows = [dict(row) for row in cur.fetchall()]
        columns = [d[0] for d in cur.description] if cur.description else []
        return columns, rows
    finally:
        conn.close()
