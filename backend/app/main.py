from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.api_v1.api import api_router
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup events
    print("🚀 File2Learning is starting up...")
    yield
    # Shutdown events  
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered learning assistant that converts documents into interactive learning materials",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    redirect_slashes=False  # Disable automatic redirect for trailing slashes
)
os.makedirs("app/static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS middleware
_default_origins = {
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
}

# Merge with settings.ALLOWED_HOSTS (which may come from env)
allowed_hosts = getattr(settings, "ALLOWED_HOSTS", []) or []
_default_origins.update(host.strip() for host in allowed_hosts if host)

# Remove duplicates and None values
origins = sorted(filter(None, _default_origins))

# Allow all origins if explicitly configured via ALLOWED_HOSTS
allow_all = "*" in allowed_hosts

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else origins,
    allow_origin_regex=".*" if allow_all else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "🎯 File2Learning API",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "healthy"
    }

@app.get("/test-cors")
def test_cors():
    return {"message": "CORS is working"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-learning-material-api"}
