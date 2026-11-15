"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, subscription, news, reports, pipeline

app = FastAPI(
    title="IntelliBrief API",
    description="AI Personalized Finance & Technology News Assistant",
    version="0.1.0",
)

# CORS middleware to allow local frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.app_base_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(subscription.router)
app.include_router(news.router)
app.include_router(reports.router)
app.include_router(pipeline.router)


@app.get("/")
def root():
    """Root endpoint welcoming visitors."""
    return {
        "app": "IntelliBrief API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "online",
    }
