from fastapi import APIRouter, HTTPException, Depends, Header, status
from typing import Optional
from datetime import datetime, timedelta

from .schemas import (
    CrawlRequest, CrawlResponse, 
    SearchResponse, JobStatusResponse, 
    JobPriority, JobStatus
)
from .services import queue_service, search_service, job_store, QueueService, SearchEngine, JobStore

router = APIRouter()

# --- Dependencies ---
# Logic: Common dependency for Rate Limiting or Auth
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    # In prod, decode JWT here
    return True

# --- 1. Search Endpoint ---
@router.get("/search", response_model=SearchResponse)
async def search_pages(
    q: str, 
    limit: int = 10, 
    cursor: Optional[str] = None,
    # Injecting service allows for easy testing mocks later
    engine: SearchEngine = Depends(lambda: search_service)
):
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    start_time = datetime.now()
    
    # Call the service layer (The "Read Path" in architecture)
    results = await engine.query(q, limit, cursor)
    
    execution_time = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        "data": results["hits"],
        "meta": {
            "total_hits": results["total"],
            "next_cursor": results["next_cursor"],
            "execution_time_ms": execution_time
        }
    }

# --- 2. Crawl Endpoint (The SLA Critical Path) ---
@router.post(
    "/crawl", 
    response_model=CrawlResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_token)] # Auth required for writes
)
async def request_recrawl(
    payload: CrawlRequest,
    queue: QueueService = Depends(lambda: queue_service)
):
    """
    Accepts a crawl request and offloads it to the High Priority Queue.
    Returns immediately with 202 Accepted.
    """
    # 1. Push to Kafka (Async I/O)
    job_id = await queue.push_job(str(payload.url), JobPriority.HIGH)
    
    # 2. Calculate SLA (1 hour from now)
    sla_time = datetime.now() + timedelta(hours=1)
    
    # 3. Return Job ID immediately
    return {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "priority": JobPriority.HIGH,
        "estimated_completion": sla_time
    }

# --- 3. Job Status Endpoint ---
@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    store: JobStore = Depends(lambda: job_store)
):
    job_data = await store.get_status(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job_data