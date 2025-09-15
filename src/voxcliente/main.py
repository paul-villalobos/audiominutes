"""Main FastAPI application for VoxCliente."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from voxcliente.config import settings
from voxcliente.api import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend para convertir grabaciones de audio en actas de reuniones profesionales mediante IA",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.voxcliente.com"]
    )
    
    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    
    # Serve index.html at root
    @app.get("/")
    async def read_index():
        return FileResponse("src/voxcliente/static/index.html")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="src/voxcliente/static"), name="static")
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "voxcliente.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
