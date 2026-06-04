import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 测试环境禁用限流：禁用路由装饰器使用的 limiter 实例
from app.limiter import limiter as app_limiter
app_limiter.enabled = False
app.state.limiter = app_limiter
app.dependency_overrides[get_db] = override_get_db



@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    client.post("/auth/register", json={"username": "testuser", "password": "testpass123"})
    res = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    token = res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
