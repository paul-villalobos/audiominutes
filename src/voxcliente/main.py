"""Main FastAPI application for VoxCliente."""

import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from posthog import Posthog

from voxcliente.config import settings
from voxcliente.api import router as health_router
from voxcliente.database import get_db_pool, close_db_pool

# Configurar logging detallado para EasyPanel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Para EasyPanel logs
        logging.FileHandler('app.log', mode='a')  # Log local también
    ]
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    logger.info(f"Iniciando aplicación {settings.app_name} v{settings.app_version}")
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Backend para convertir grabaciones de audio en actas de reuniones profesionales mediante IA",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Middleware de logging de requests
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error en request {request.method} {request.url}: {str(e)}", exc_info=True)
            raise
    
    # Manejo global de errores de validación
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Error de validación en {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Error de validación", "errors": exc.errors()}
        )
    
    # Manejo global de errores generales
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Error no manejado en {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error interno del servidor: {str(exc)}"}
        )
    
    # Initialize PostHog
    try:
        posthog = Posthog(settings.posthog_api_key, host=settings.posthog_host)
        app.state.posthog = posthog
        logger.info("PostHog inicializado correctamente")
    except Exception as e:
        logger.error(f"Error inicializando PostHog: {str(e)}")
        # Crear un mock para que la app no falle
        app.state.posthog = None
    
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
        allowed_hosts=["localhost", "127.0.0.1", "voxcliente.com"]
    )
    
    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    logger.info("Router de API incluido")
    
    # Serve index.html at root
    @app.get("/")
    async def read_index():
        try:
            return FileResponse("src/voxcliente/static/index.html")
        except Exception as e:
            logger.error(f"Error sirviendo index.html: {str(e)}")
            raise
    
    # Mount static files
    try:
        app.mount("/static", StaticFiles(directory="src/voxcliente/static"), name="static")
        logger.info("Archivos estáticos montados correctamente")
    except Exception as e:
        logger.error(f"Error montando archivos estáticos: {str(e)}")
        raise
    
    # Database startup/shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Initialize database connection."""
        try:
            await get_db_pool()
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """Close database connection."""
        try:
            await close_db_pool()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {str(e)}")
    
    logger.info("Aplicación configurada correctamente")
    return app


# Create the app instance
try:
    app = create_app()
    logger.info("Instancia de aplicación creada exitosamente")
except Exception as e:
    logger.error(f"Error crítico creando aplicación: {str(e)}", exc_info=True)
    raise


if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor Uvicorn...")
    try:
        uvicorn.run(
            "voxcliente.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Error iniciando servidor: {str(e)}", exc_info=True)
        raise
