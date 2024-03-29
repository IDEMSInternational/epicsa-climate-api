import pytest
from typing import Generator

from fastapi.testclient import TestClient
from .test_main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
