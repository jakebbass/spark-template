"""FastAPI backend for AI Fantasy Draft Assistant."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_rankings import router as rankings_router
from app.api.routes_draft import router as draft_router
from app.api.routes_advice import router as advice_router
from app.core.config import settings

app = FastAPI(
    title="Fantasy Assistant API",
    description="AI-powered fantasy football draft assistant",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rankings_router, prefix="/rankings", tags=["rankings"])
app.include_router(draft_router, prefix="/draft", tags=["draft"])  
app.include_router(advice_router, prefix="/advice", tags=["advice"])


@app.get("/healthz")
async def health_check() -> dict[str, bool]:
    """Health check endpoint."""
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)