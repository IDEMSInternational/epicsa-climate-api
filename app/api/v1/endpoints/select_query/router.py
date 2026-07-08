import json
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.config import Settings

from .schema import SelectQueryRequest, SelectQueryResponse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import pool as psycopg2_pool
except Exception:  # pragma: no cover - covered by runtime behavior
    psycopg2 = None
    RealDictCursor = None
    psycopg2_pool = None


router = APIRouter()
_STATEMENT_TIMEOUT_MS = 5000
_POOL_MIN_CONNECTIONS = 1
_POOL_MAX_CONNECTIONS = 10
_POOL_LOCK = Lock()
_CONNECTION_POOL = None
_CONNECTION_POOL_KEY: tuple[Any, ...] | None = None

_TABLE_CONFIG: dict[str, dict[str, Any]] = {
    "crop": {
        "from": "crop",
        "station_filter": "crop.station_id = %s",
        "columns": {
            "station_id": "crop.station_id AS station_id",
            "year": "crop.year AS year",
            "plant_day": "crop.plant_day AS plant_day",
            "plant_length": "crop.plant_length AS plant_length",
            "rain_total": "crop.rain_total AS rain_total",
            "include_start_condition": "crop.include_start_condition AS include_start_condition",
            "summary_type": "crop.summary_type AS summary_type",
            "summary_element": "crop.summary_element AS summary_element",
            "summary_value": "crop.summary_value AS summary_value",
            "definition_id": "crop.definition_id AS definition_id",
            "status": "crop.status AS status",
            "time_stamp": "crop.time_stamp AS time_stamp",
        },
        "orderable": {
            "time_stamp": "crop.time_stamp",
            "year": "crop.year",
        },
        "default_order": "time_stamp",
    },
    "definition": {
        "from": "definition d JOIN summary s ON s.definition_id = d.definition_id",
        "station_filter": "s.station_id = %s",
        "columns": {
            "definition_id": "d.definition_id AS definition_id",
            "time_stamp": "d.time_stamp AS time_stamp",
            "summary_element": "d.summary_element AS summary_element",
            "summary_type": "d.summary_type AS summary_type",
            "definition_value": "d.definition_value AS definition_value",
            "accreditation": "d.accreditation AS accreditation",
        },
        "orderable": {
            "time_value": "s.time_value",
            "time_stamp": "d.time_stamp",
        },
        "default_order": "time_value",
    },
    "station": {
        "from": "station",
        "station_filter": "station.station_id = %s",
        "columns": {
            "station_id": "station.station_id AS station_id",
            "station_name": "station.station_name AS station_name",
            "latitude": "station.latitude AS latitude",
            "longitude": "station.longitude AS longitude",
            "elevation": "station.elevation AS elevation",
            "district": "station.district AS district",
            "country_code": "station.country_code AS country_code",
            "time_stamp": "station.time_stamp AS time_stamp",
            "status": "station.status AS status",
        },
        "orderable": {
            "time_stamp": "station.time_stamp",
        },
        "default_order": "time_stamp",
    },
    "summary": {
        "from": "summary",
        "station_filter": "summary.station_id = %s",
        "columns": {
            "station_id": "summary.station_id AS station_id",
            "definition_id": "summary.definition_id AS definition_id",
            "time_type": "summary.time_type AS time_type",
            "time_value": "summary.time_value AS time_value",
            "summary_type": "summary.summary_type AS summary_type",
            "summary_element": "summary.summary_element AS summary_element",
            "summary_name": "summary.summary_name AS summary_name",
            "summary_value": "summary.summary_value AS summary_value",
            "time_stamp": "summary.time_stamp AS time_stamp",
            "status": "summary.status AS status",
        },
        "orderable": {
            "time_value": "summary.time_value",
            "time_stamp": "summary.time_stamp",
        },
        "default_order": "time_value",
    },
    "summary_station_metadata": {
        "from": "summary_station_metadata",
        "station_filter": "summary_station_metadata.station_id = %s",
        "columns": {
            "station_id": "summary_station_metadata.station_id AS station_id",
            "summary_type": "summary_station_metadata.summary_type AS summary_type",
            "definition_id": "summary_station_metadata.definition_id AS definition_id",
            "time_stamp": "summary_station_metadata.time_stamp AS time_stamp",
        },
        "orderable": {
            "time_stamp": "summary_station_metadata.time_stamp",
        },
        "default_order": "time_stamp",
    },
}


def _build_select_query(payload: SelectQueryRequest) -> tuple[str, list[Any]]:
    table_config = _TABLE_CONFIG[payload.table_name]
    available_columns: dict[str, str] = table_config["columns"]

    selected_columns = payload.columns or list(available_columns.keys())
    unknown_columns = [column for column in selected_columns if column not in available_columns]
    if unknown_columns:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported columns for table '{payload.table_name}': "
                f"{', '.join(unknown_columns)}"
            ),
        )

    orderable: dict[str, str] = table_config["orderable"]
    order_key = payload.order_by or table_config["default_order"]
    if order_key not in orderable:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported order_by '{order_key}' for table '{payload.table_name}'. "
                f"Allowed values: {', '.join(orderable.keys())}"
            ),
        )

    order_direction = "ASC" if payload.order_direction == "asc" else "DESC"
    select_clause = ", ".join(available_columns[column] for column in selected_columns)
    sql = (
        f"SELECT {select_clause} "
        f"FROM {table_config['from']} "
        f"WHERE {table_config['station_filter']} "
        f"ORDER BY {orderable[order_key]} {order_direction} "
        "LIMIT %s"
    )
    return sql, [payload.station_id, payload.max_rows]

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


def _pool_key_from_secret(secret: dict[str, Any]) -> tuple[Any, ...]:
    return (
        secret["host"],
        secret["port"],
        secret["dbname"],
        secret["user"],
        secret["password"],
        secret.get("sslmode", "prefer"),
    )


def _get_connection_pool(secret: dict[str, Any]):
    global _CONNECTION_POOL
    global _CONNECTION_POOL_KEY

    if psycopg2_pool is None:
        raise RuntimeError("psycopg2 is not installed. Add psycopg2-binary to requirements.")

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
    global _CONNECTION_POOL
    global _CONNECTION_POOL_KEY

    with _POOL_LOCK:
        if _CONNECTION_POOL is not None:
            _CONNECTION_POOL.closeall()
            _CONNECTION_POOL = None
            _CONNECTION_POOL_KEY = None


def execute_select_query(
    sql: str,
    params: list[Any],
    secret: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    if psycopg2 is None or RealDictCursor is None:
        raise RuntimeError("psycopg2 is not installed. Add psycopg2-binary to requirements.")

    pool = _get_connection_pool(secret)
    connection = None
    try:
        connection = pool.getconn()
        connection.set_session(readonly=True, autocommit=False)
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SET LOCAL statement_timeout = %s", (_STATEMENT_TIMEOUT_MS,))
            cursor.execute(sql, tuple(params))
            rows = [dict(row) for row in cursor.fetchall()]
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


@router.post("/", response_model=SelectQueryResponse)
def run_select_query(payload: SelectQueryRequest) -> SelectQueryResponse:
    sql, params = _build_select_query(payload)

    settings = Settings()
    secret = _load_db_secret(settings.POSTGRES_SECRET_FILE)

    try:
        columns, rows = execute_select_query(
            sql=sql,
            params=params,
            secret=secret,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail="Postgres query failed.") from error

    return SelectQueryResponse(columns=columns, row_count=len(rows), rows=rows)
