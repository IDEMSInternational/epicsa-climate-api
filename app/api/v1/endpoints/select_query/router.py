import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.config import Settings

from .schema import SelectQueryRequest, SelectQueryResponse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:  # pragma: no cover - covered by runtime behavior
    psycopg2 = None
    RealDictCursor = None


router = APIRouter()
_DISALLOWED_SQL_KEYWORDS = (
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
    "comment",
    "copy",
    "vacuum",
    "analyze",
    "refresh",
    "merge",
    "call",
    "do",
)


def _is_read_only_sql(sql: str) -> bool:
    no_block_comments = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    no_line_comments = re.sub(r"--.*?$", " ", no_block_comments, flags=re.M)
    normalized = no_line_comments.strip().lower()

    if not normalized.startswith("select"):
        return False

    if ";" in normalized.rstrip(";"):
        return False

    disallowed_pattern = r"\b(" + "|".join(_DISALLOWED_SQL_KEYWORDS) + r")\b"
    return re.search(disallowed_pattern, normalized) is None


def _load_db_secret(secret_file_path: str) -> dict[str, Any]:
    secret_path = Path(secret_file_path)
    if not secret_path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                f"Postgres secret file not found at '{secret_file_path}'. "
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


def execute_select_query(
    sql: str,
    params: list[Any],
    max_rows: int,
    secret: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    if psycopg2 is None or RealDictCursor is None:
        raise RuntimeError("psycopg2 is not installed. Add psycopg2-binary to requirements.")

    connection = psycopg2.connect(
        host=secret["host"],
        port=secret["port"],
        dbname=secret["dbname"],
        user=secret["user"],
        password=secret["password"],
        sslmode=secret.get("sslmode", "prefer"),
    )
    try:
        connection.set_session(readonly=True, autocommit=True)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, tuple(params))
            rows = [dict(row) for row in cursor.fetchmany(max_rows)]
            columns = [column.name for column in cursor.description] if cursor.description else []
            return columns, rows
    finally:
        connection.close()


@router.post("/", response_model=SelectQueryResponse)
def run_select_query(payload: SelectQueryRequest) -> SelectQueryResponse:
    if not _is_read_only_sql(payload.sql):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT SQL is allowed.",
        )

    settings = Settings()
    secret = _load_db_secret(settings.POSTGRES_SECRET_FILE)

    try:
        columns, rows = execute_select_query(
            sql=payload.sql,
            params=payload.params,
            max_rows=payload.max_rows,
            secret=secret,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Postgres query failed: {error}") from error

    return SelectQueryResponse(columns=columns, row_count=len(rows), rows=rows)
