"""Main FastAPI application entry point with static file serving for src/."""

from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
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
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health.router)
app.include_router(subscription.router)
app.include_router(news.router)
app.include_router(reports.router)
app.include_router(pipeline.router)

# Path to the frontend files in src/
SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the frontend single page app from src/index.html."""
    index_file = SRC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>IntelliBrief API Online</h1><p>Visit /docs for API documentation.</p>")


@app.get("/styles.css")
def serve_styles():
    """Serve custom stylesheet from src/styles.css."""
    css_file = SRC_DIR / "styles.css"
    if css_file.exists():
        return Response(content=css_file.read_text(encoding="utf-8"), media_type="text/css")
    return Response(status_code=404)


@app.get("/app.js")
def serve_script():
    """Serve frontend javascript logic from src/app.js."""
    js_file = SRC_DIR / "app.js"
    if js_file.exists():
        return Response(content=js_file.read_text(encoding="utf-8"), media_type="application/javascript")
    return Response(status_code=404)
