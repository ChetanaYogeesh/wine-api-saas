import os
import sys
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ["API_KEY"] = "test-api-key"
os.environ["ALLOWED_ORIGINS"] = "*"

TEST_WINES = [
    {
        "id": 0,
        "name": "Test Red Wine 2020",
        "region": "Napa Valley",
        "variety": "Red Wine",
        "rating": 92.0,
        "notes": "A test wine with notes of cherry and oak.",
    },
    {
        "id": 1,
        "name": "Test White Wine 2021",
        "region": "Sonoma",
        "variety": "White Wine",
        "rating": 88.0,
        "notes": "A crisp white wine with apple and citrus notes.",
    },
    {
        "id": 2,
        "name": "Test Rosé 2022",
        "region": "Provence",
        "variety": "Rose Wine",
        "rating": 85.0,
        "notes": "Light and refreshing with strawberry flavors.",
    },
    {
        "id": 3,
        "name": "Test Pinot Noir 2019",
        "region": "Willamette Valley",
        "variety": "Red Wine",
        "rating": 95.0,
        "notes": "An elegant Pinot with dark fruit and earthy undertones.",
    },
    {
        "id": 4,
        "name": "Test Bordeaux 2018",
        "region": "Bordeaux",
        "variety": "Red Wine",
        "rating": 91.0,
        "notes": "A classic Bordeaux with plum and spice.",
    },
]


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite:///{path}"
    yield
    try:
        os.unlink(path)
    except Exception:
        pass


@pytest.fixture(scope="session")
def test_engine():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    from app.models import User, APIKey, Wine

    engine = create_engine(
        os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(
        id=1,
        email="test@example.com",
        hashed_password="$2b$12$testhash",
        full_name="Test User",
    )
    session.add(user)

    api_key = APIKey(
        id=1,
        key="test-api-key",
        name="Test Key",
        user_id=1,
        is_active=True,
        rate_limit=60,
        monthly_limit=10000,
        tier="free",
    )
    session.add(api_key)

    for wine_data in TEST_WINES:
        session.add(Wine(**wine_data))

    session.commit()
    session.close()

    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_engine):
    from sqlalchemy.orm import sessionmaker
    from fastapi.testclient import TestClient
    from app.models import Wine, UsageLog

    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()

    try:
        session.query(UsageLog).delete()
    except Exception:
        pass

    session.query(Wine).delete()
    for wine_data in TEST_WINES:
        session.add(Wine(**wine_data))
    session.commit()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    from app.main import app
    from app.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    session.close()
    app.dependency_overrides.clear()


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def auth_headers(api_key):
    return {"X-API-Key": api_key}
