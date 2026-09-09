main_content = """from fastapi import FastAPI, Request
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

# Include API v1 routes first
app.include_router(api_router, prefix="/api/v1")

# Serve docs directory
if os.path.exists("docs"):
    app.mount("/docs-portal", StaticFiles(directory="docs", html=True), name="docs_portal")

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
"""

with open("backend/app/main.py", "w", encoding="utf-8") as f:
    f.write(main_content)

print("Updated backend/app/main.py with optimal router and UI serving order.")
