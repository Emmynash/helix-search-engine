from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .security import validate_url_safety

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobPriority(str, Enum):
    HIGH = "high"
    LOW = "low"

class CrawlRequest(BaseModel):
    url: HttpUrl
    depth: int = Field(default=1, ge=1, le=3, description="Recursion depth (max 3)")
    
    @field_validator('url')
    def validate_security(cls, v):
        # Delegate to the robust security module
        validate_url_safety(str(v))
        return v

class CrawlResponse(BaseModel):
    job_id: str
    status: JobStatus
    priority: JobPriority
    estimated_completion: datetime
    queue_position: Optional[int] = None  # Transparency for the user

class SearchResult(BaseModel):
    id: str
    title: str
    url: HttpUrl
    snippet: str
    score: float

class SearchResponse(BaseModel):
    data: List[SearchResult]
    meta: dict

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None