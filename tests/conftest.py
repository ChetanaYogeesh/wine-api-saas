import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["API_KEY"] = "test-api-key"
os.environ["ALLOWED_ORIGINS"] = "*"

TEST_DATA_PATH = Path(__file__).parent.parent / "test_data.csv"


@pytest.fixture(scope="function")
def reset_data():
    from app import data

    original_path = data.DATA_PATH
    data.DATA_PATH = TEST_DATA_PATH
    data._df = None
    yield
    data._df = None
    data.DATA_PATH = original_path


@pytest.fixture
def client(reset_data):
    from app.main import app

    return TestClient(app)


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def auth_headers(api_key):
    return {"X-API-Key": api_key}
