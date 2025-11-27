from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

# --- Enums for strict typing ---
class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobPriority(str, Enum):
    HIGH = "high"       # User requested (SLA)
    LOW = "low"         # Background crawl

# --- Request Models ---
class CrawlRequest(BaseModel):
    url: HttpUrl
    depth: int = Field(default=1, ge=1, le=3, description="Depth restricted to 3 for performance")
    
    @field_validator('url')
    def validate_domain(cls, v):
        # Senior Dev Logic: Block internal IPs or known bad actors here
        if "localhost" in str(v):
            raise ValueError("Cannot crawl local networks")
        return v

# --- Response Models ---
class CrawlResponse(BaseModel):
    job_id: str
    status: JobStatus
    priority: JobPriority
    estimated_completion: datetime

class SearchResult(BaseModel):
    id: str
    title: str
    url: HttpUrl
    snippet: str
    score: float

class SearchResponse(BaseModel):
    data: List[SearchResult]
    meta: dict  # Contains cursor, total_hits, execution_time

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None