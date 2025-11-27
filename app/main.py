from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router as api_router

app = FastAPI(
    title="Atlas Search Core API",
    version="1.0.0",
    description="Scalable Search Engine Backend"
)

# Logic: strict CORS settings are mandatory for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dashboard.atlas-search.com"], # Never use "*" in prod
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)