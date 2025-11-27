import uuid
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
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    return True

# --- Search Endpoint ---
@router.get("/search", response_model=SearchResponse)
async def search_pages(
    q: str, 
    limit: int = 10, 
    cursor: Optional[str] = None,
    engine: SearchEngine = Depends(lambda: search_service)
):
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    start_time = datetime.now()
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

# --- Crawl Endpoint (Fixed) ---
@router.post(
    "/crawl", 
    response_model=CrawlResponse, 
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_token)]
)
async def request_recrawl(
    payload: CrawlRequest,
    queue: QueueService = Depends(lambda: queue_service),
    store: JobStore = Depends(lambda: job_store)
):
    # 1. Generate ID (The API is the source of truth for IDs)
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    
    # 2. FIX: Write to DB FIRST (Guarantees no 404s on immediate poll)
    await store.create_job(job_id, JobStatus.QUEUED)
    
    # 3. Check System Load for SLA Calculation
    q_depth = await queue.get_queue_depth(JobPriority.HIGH)
    
    # Dynamic SLA Logic: 
    # Assume 1 second processing time per job + 30s buffer.
    # If queue is deep, this time moves further out, being honest with the user.
    estimated_seconds = (q_depth * 1.0) + 30
    sla_time = datetime.now() + timedelta(seconds=estimated_seconds)

    # 4. Push to Queue (With Circuit Breaker logic)
    success = await queue.push_job(job_id, str(payload.url), JobPriority.HIGH)
    
    if not success:
        # Rollback or Mark Failed if Queue is down
        await store.create_job(job_id, JobStatus.FAILED)
        raise HTTPException(
            status_code=503, 
            detail="Ingestion queue unavailable. Please try again later."
        )
    
    return {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "priority": JobPriority.HIGH,
        "estimated_completion": sla_time,
        "queue_position": q_depth
    }

# --- Job Status Endpoint ---
@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    store: JobStore = Depends(lambda: job_store)
):
    job_data = await store.get_status(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job_data