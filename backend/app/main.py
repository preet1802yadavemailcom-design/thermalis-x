from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from backend.app.config import settings
from backend.app.api.v1.router import api_router
from backend.app.core.logging import logger
from backend.app.db.session import engine
from backend.app.db.base import Base

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM & Satellite Data",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware (STRIDE Defense-in-Depth)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Include API v1 routes first
app.include_router(api_router, prefix="/api/v1")

# Serve docs directory
if os.path.exists("docs"):
    app.mount("/docs-portal", StaticFiles(directory="docs", html=True), name="docs_portal")

# Root Health check route
@app.get("/health")
async def root_health():
    return {
        "status": "READY",
        "app_version": settings.APP_VERSION,
        "components": {"system": "HEALTHY", "database": "HEALTHY"}
    }

@app.get("/docs-hub")
@app.get("/documentation")
async def docs_hub_redirect():
    if os.path.exists("docs/index.html"):
        return FileResponse("docs/index.html")
    return {"message": "Documentation portal available at /docs-portal/index.html"}

# Root UI route
@app.get("/")
async def root_index():
    index_path = os.path.join("frontend", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"{settings.APP_NAME} API Online. Visit /docs for OpenAPI documentation."}

@app.get("/index.html")
async def root_index_file():
    index_path = os.path.join("frontend", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": f"{settings.APP_NAME} API Online."}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": "SYS_500", "message": "An internal error occurred in the THERMALIS-X analytics engine."}
    )
