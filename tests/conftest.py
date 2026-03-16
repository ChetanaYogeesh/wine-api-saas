import os
import sys
import pytest
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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


@pytest.fixture(scope="session")
def test_db_url():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield f"sqlite:///{path}"
    os.unlink(path)


@pytest.fixture(scope="session")
def setup_test_db(test_db_url):
    engine = create_engine(
        test_db_url, connect_args={"check_same_thread": False}, echo=False
    )

    from app.database import Base
    from app.models import User, APIKey, Wine

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
        wine = Wine(**wine_data)
        session.add(wine)

    session.commit()
    session.close()

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def test_session(setup_test_db):

    engine = setup_test_db
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture(scope="function")
def client(test_session):
    from fastapi.testclient import TestClient
    from app import database
    from app.models import Wine, UsageLog
    from app.database import get_db

    try:
        test_session.query(UsageLog).delete()
    except Exception:
        pass

    for wine in test_session.query(Wine).all():
        test_session.delete(wine)
    for wine_data in TEST_WINES:
        wine = Wine(**wine_data)
        test_session.add(wine)

    test_session.commit()

    TestSessionLocal = sessionmaker(
        bind=test_session.get_bind(), autocommit=False, autoflush=False
    )

    def _get_test_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    from app.main import app

    app.dependency_overrides[get_db] = _get_test_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def auth_headers(api_key):
    return {"X-API-Key": api_key}
