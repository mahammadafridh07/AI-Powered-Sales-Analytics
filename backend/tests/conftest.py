import os
import sys
import tempfile
import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Ensure app package importable and use an isolated SQLite DB for tests
TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "test_sales_analytics.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ["JWT_SECRET"] = "test-secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

from app.main import app  # noqa: E402
from app.database.session import Base, engine, SessionLocal  # noqa: E402
from app.services import upload_service  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")


@pytest.fixture(scope="session", autouse=True)
def _setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    csv_path = os.path.join(DATA_DIR, "sample_sales.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df["order_date"] = pd.to_datetime(df["order_date"])
        cleaned = upload_service.clean(df)
        upload_service.ingest(db, cleaned)
    db.close()
    yield
    
    engine.dispose()
    
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def auth_token(client):
    email = "tester@example.com"
    password = "TestPass123"
    res = client.post("/auth/register", json={"name": "Tester", "email": email, "password": password})
    if res.status_code != 201:
        res = client.post("/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


@pytest.fixture()
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}
