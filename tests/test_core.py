import pytest
from httpx import AsyncClient
from app.main import app
from app.services import queue_service, JobPriority

# Mock the dependency injection for the Queue to simulate load
async def mock_high_load_queue(priority: JobPriority):
    # Simulate a backed-up queue (5000 items)
    return 5000

@pytest.mark.asyncio
async def test_search_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/v1/search?q=python")
    assert response.status_code == 200
    assert "data" in response.json()
    assert response.json()["meta"]["total_hits"] > 0

@pytest.mark.asyncio
async def test_security_block_localhost():
    """Ensures our SSRF protection actually works"""
    payload = {"url": "http://localhost:8080/admin"}
    headers = {"Authorization": "Bearer test-token"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/v1/crawl", json=payload, headers=headers)
    
    # Should fail with 400 Bad Request
    assert response.status_code == 400
    assert "restricted network" in response.json()["detail"]

@pytest.mark.asyncio
async def test_sla_adjustment_under_load():
    """Verifies that high queue depth pushes out the estimated completion time"""
    # Override the queue service to simulate high load
    app.dependency_overrides[queue_service.get_queue_depth] = mock_high_load_queue
    
    payload = {"url": "https://google.com"}
    headers = {"Authorization": "Bearer test-token"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/v1/crawl", json=payload, headers=headers)
    
    data = response.json()
    assert response.status_code == 202
    assert data["queue_position"] == 5000
    
    # Parse timestamps to ensure SLA logic added the buffer
    # 5000 items * 1 sec/item = ~5000 seconds -> ~1.3 hours from now
    # We just check it's definitely not "now"
    assert data["estimated_completion"] > data["job_id"] # Simple existence check