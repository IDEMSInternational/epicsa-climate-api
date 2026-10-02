import json
from pathlib import Path
import tempfile
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import psycopg
from psycopg_pool import ConnectionPool, PoolTimeout

from app.core.config import Settings
from app.core import database
from app.main import app


def test_load_db_secret_success(tmp_path):
    secret_data = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_db",
        "user": "test_user",
        "password": "test_password",
    }
    secret_file = tmp_path / "postgres-secret.json"
    secret_file.write_text(json.dumps(secret_data), encoding="utf-8")

    loaded = database.load_db_secret(str(secret_file))
    assert loaded["host"] == "localhost"
    assert loaded["dbname"] == "test_db"
    assert loaded["user"] == "test_user"


def test_load_db_secret_missing_file():
    with pytest.raises(database.HTTPException) as exc_info:
        database.load_db_secret("/non/existent/secret.json")
    assert exc_info.value.status_code == 500
    assert "not found" in exc_info.value.detail.lower()


def test_load_db_secret_missing_keys(tmp_path):
    secret_data = {
        "host": "localhost",
        "port": 5432,
        # missing dbname, user, password
    }
    secret_file = tmp_path / "invalid-secret.json"
    secret_file.write_text(json.dumps(secret_data), encoding="utf-8")

    with pytest.raises(database.HTTPException) as exc_info:
        database.load_db_secret(str(secret_file))
    assert exc_info.value.status_code == 500
    assert "missing required keys" in exc_info.value.detail.lower()


def test_connection_pool_initialization_and_close():
    secret = {
        "host": "localhost",
        "port": 5432,
        "dbname": "test_db",
        "user": "test_user",
        "password": "test_password",
        "sslmode": "disable",
    }

    pool = database.get_connection_pool(secret)
    assert pool is not None
    assert isinstance(pool, ConnectionPool)
    assert pool.max_size == Settings().POSTGRES_POOL_MAX_CONNECTIONS

    # Repeated calls return the same pool
    assert database.get_connection_pool(secret) is pool

    # Close pool
    database.close_connection_pool()
    assert database._CONNECTION_POOL is None


def test_pool_timeout_exception_handler():
    test_app = FastAPI()
    test_app.add_exception_handler(
        PoolTimeout,
        app.exception_handlers[PoolTimeout],
    )

    @test_app.get("/trigger-pool-timeout")
    def trigger():
        raise PoolTimeout("pool timed out waiting for connection")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/trigger-pool-timeout")

    assert response.status_code == 503
    assert response.headers.get("retry-after") == "2"
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "DATABASE_BUSY"
    assert body["error"]["retryable"] is True


def test_statement_timeout_exception_handler():
    test_app = FastAPI()
    test_app.add_exception_handler(
        psycopg.Error,
        app.exception_handlers[psycopg.Error],
    )

    @test_app.get("/trigger-statement-timeout")
    def trigger():
        raise psycopg.OperationalError("canceling statement due to statement timeout")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/trigger-statement-timeout")

    assert response.status_code == 504
    body = response.json()
    assert body["error"]["code"] == "QUERY_TIMEOUT"
    assert body["error"]["retryable"] is True


def test_generic_database_error_exception_handler():
    test_app = FastAPI()
    test_app.add_exception_handler(
        psycopg.Error,
        app.exception_handlers[psycopg.Error],
    )

    @test_app.get("/trigger-db-error")
    def trigger():
        raise psycopg.ProgrammingError("relation does not exist")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/trigger-db-error")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "DATABASE_ERROR"
    assert body["error"]["retryable"] is False


def test_unhandled_exception_returns_json_not_plain_text():
    test_app = FastAPI()
    test_app.add_exception_handler(
        Exception,
        app.exception_handlers[Exception],
    )

    @test_app.get("/trigger-unhandled")
    def trigger():
        raise RuntimeError("unexpected failure")

    client = TestClient(test_app, raise_server_exceptions=False)
    response = client.get("/trigger-unhandled")

    assert response.status_code == 500
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
