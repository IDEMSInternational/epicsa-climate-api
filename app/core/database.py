import json
import os
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException
from app.core.config import Settings

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool as psycopg2_pool
except ImportError:  # pragma: no cover
    psycopg2 = None
    RealDictCursor = None
    psycopg2_pool = None

_STATEMENT_TIMEOUT_MS = 5000
_POOL_MIN_CONNECTIONS = 1
_POOL_MAX_CONNECTIONS = 10
_POOL_LOCK = Lock()
_CONNECTION_POOL = None
_CONNECTION_POOL_KEY: Optional[Tuple[Any, ...]] = None


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

    try:
        secret = json.loads(secret_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"Postgres secret file is not valid JSON: {error}",
        ) from error

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

    if psycopg2_pool is None:
        raise RuntimeError("psycopg2 is not installed. Add psycopg2-binary to dependencies.")

    if secret is None:
        secret = load_db_secret()

    pool_key = _pool_key_from_secret(secret)
    with _POOL_LOCK:
        if _CONNECTION_POOL is not None and _CONNECTION_POOL_KEY != pool_key:
            _CONNECTION_POOL.closeall()
            _CONNECTION_POOL = None
            _CONNECTION_POOL_KEY = None

        if _CONNECTION_POOL is None:
            _CONNECTION_POOL = psycopg2_pool.ThreadedConnectionPool(
                minconn=_POOL_MIN_CONNECTIONS,
                maxconn=_POOL_MAX_CONNECTIONS,
                host=secret["host"],
                port=secret["port"],
                dbname=secret["dbname"],
                user=secret["user"],
                password=secret["password"],
                connect_timeout=10,
                sslmode=secret.get("sslmode", "prefer"),
            )
            _CONNECTION_POOL_KEY = pool_key

        return _CONNECTION_POOL


def close_connection_pool() -> None:
    """Close all open connections in the pool on application shutdown."""
    global _CONNECTION_POOL, _CONNECTION_POOL_KEY

    with _POOL_LOCK:
        if _CONNECTION_POOL is not None:
            _CONNECTION_POOL.closeall()
            _CONNECTION_POOL = None
            _CONNECTION_POOL_KEY = None


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

    if psycopg2 is None or RealDictCursor is None:
        raise RuntimeError("psycopg2 is not installed. Add psycopg2-binary to requirements.")

    pool = get_connection_pool(secret)
    connection = None
    try:
        connection = pool.getconn()
        connection.set_session(readonly=True, autocommit=False)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SET LOCAL statement_timeout = %s", (_STATEMENT_TIMEOUT_MS,))
            cursor.execute(sql, tuple(params))
            rows = [dict(row) for row in cursor.fetchall()] if cursor.description else []
            columns = [column.name for column in cursor.description] if cursor.description else []
            connection.rollback()
            return columns, rows
    except Exception:
        if connection is not None:
            try:
                connection.rollback()
            except Exception:
                pass
        raise
    finally:
        if connection is not None:
            pool.putconn(connection)


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
