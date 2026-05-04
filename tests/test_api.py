import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)
HEADERS = {"changeme-use-a-long-random-string": settings.api_key}

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "infra-pulse"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_port_check_requires_key():
    r = client.get("/api/v1/check/port/1.1.1.1/80")
    assert r.status_code == 401

def test_port_check_invalid_port():
    r = client.get("/api/v1/check/port/1.1.1.1/99999", headers=HEADERS)
    assert r.status_code == 400

def test_port_check_valid():
    r = client.get("/api/v1/check/port/1.1.1.1/80", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "reachable" in data
    assert "latency_ms" in data
    assert "checked_at" in data

def test_batch_too_many():
    items = [{"host": "1.1.1.1", "port": 80}] * 21
    r = client.post("/api/v1/batch", json=items, headers=HEADERS)
    assert r.status_code == 400
