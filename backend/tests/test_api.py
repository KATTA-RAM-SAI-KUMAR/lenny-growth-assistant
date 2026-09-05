import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    asyncio.run(init_db())

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "online"

@pytest.mark.asyncio
async def test_health_probe():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "database" in data
        assert "ollama" in data
        assert "retrieval" in data

@pytest.mark.asyncio
async def test_sessions_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create session
        create_resp = await client.post("/api/sessions", json={"title": "Test Session"})
        assert create_resp.status_code == 200
        session_data = create_resp.json()
        session_id = session_data["id"]
        assert session_data["title"] == "Test Session"

        # Fetch session
        get_resp = await client.get(f"/api/sessions/{session_id}")
        assert get_resp.status_code == 200

        # List sessions
        list_resp = await client.get("/api/sessions")
        assert list_resp.status_code == 200
        sessions = list_resp.json()
        assert any(s["id"] == session_id for s in sessions)

        # Delete session
        del_resp = await client.delete(f"/api/sessions/{session_id}")
        assert del_resp.status_code == 200
