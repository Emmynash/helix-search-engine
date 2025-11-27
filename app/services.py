import uuid
from datetime import datetime, timedelta
import asyncio
from .schemas import JobPriority, JobStatus

#Logic: 
# We use Abstract Base Classes (implicitly here) logic. 
# This file mocks the connections to Kafka, Redis, and Elasticsearch.
# In a real commit, these would wrap the actual client libraries.

class QueueService:
    """Interface for the Message Queue (Kafka)"""
    async def push_job(self, url: str, priority: JobPriority) -> str:
        # Simulate network latency of hitting Kafka
        await asyncio.sleep(0.05) 
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        
        # Logic: In reality, we'd serialize this to JSON and push to 
        # topic 'crawl-high-priority' or 'crawl-background'
        print(f"[Queue] Pushed {url} to {priority.value} priority topic. ID: {job_id}")
        return job_id

class SearchEngine:
    """Interface for the Inverted Index (Elasticsearch)"""
    async def query(self, q: str, limit: int, cursor: str = None) -> dict:
        # Simulate scatter-gather latency across shards
        await asyncio.sleep(0.15)
        
        # Mock Response
        return {
            "hits": [
                {
                    "id": "doc_1", 
                    "title": f"Results for {q}", 
                    "url": "https://example.com/1", 
                    "snippet": "lorem ipsum...", 
                    "score": 0.95
                }
            ],
            "total": 15400,
            "next_cursor": "dXNlcmlkXzg4"
        }

class JobStore:
    """Interface for Metadata Store (Redis/Postgres)"""
    async def get_status(self, job_id: str):
        # Simulate DB read
        await asyncio.sleep(0.02)
        
        # Mock logic to simulate SLA completion
        return {
            "job_id": job_id,
            "status": JobStatus.PROCESSING, # Mocking that it's still running
            "created_at": datetime.now()
        }

# Singleton instances for Dependency Injection
queue_service = QueueService()
search_service = SearchEngine()
job_store = JobStore()