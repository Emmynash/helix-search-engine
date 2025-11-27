import uuid
from datetime import datetime
import asyncio
from .schemas import JobPriority, JobStatus

class QueueService:
    async def get_queue_depth(self, priority: JobPriority) -> int:
        """
        Returns the approximate number of messages in the queue.
        In production, this queries Kafka Consumer Offsets.
        """
        # Mock logic: High priority usually has fewer items
        return 1500 if priority == JobPriority.HIGH else 45000

    async def push_job(self, job_id: str, url: str, priority: JobPriority) -> bool:
        """
        Pushes a job to the message broker.
        Returns True if successful, False if broker is down.
        """
        try:
            # Simulate network I/O
            await asyncio.sleep(0.05)
            # Logic: Serialize and push to topic
            # producer.send(topic, key=job_id, value=url)
            return True
        except Exception as e:
            # Senior Dev Logic: Log critical infrastructure failures
            print(f"CRITICAL: Kafka push failed for {job_id}: {e}")
            return False

class JobStore:
    def __init__(self):
        self._db = {}  # Mock In-Memory Database

    async def create_job(self, job_id: str, status: JobStatus):
        """Syncs the initial state to DB before Queue push to prevent race conditions"""
        self._db[job_id] = {
            "job_id": job_id,
            "status": status,
            "created_at": datetime.now()
        }
        return True

    async def get_status(self, job_id: str):
        return self._db.get(job_id)

class SearchEngine:
    async def query(self, q: str, limit: int, cursor: str = None) -> dict:
        # Simulate scatter-gather latency
        await asyncio.sleep(0.15)
        return {
            "hits": [],
            "total": 0,
            "next_cursor": None
        }

# Singleton instances
queue_service = QueueService()
search_service = SearchEngine()
job_store = JobStore()