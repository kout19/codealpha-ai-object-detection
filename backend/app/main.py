"""Application entry point.

Responsible ONLY for wiring: creating the FastAPI app, registering
middleware, mounting static files, including routers, and registering
global exception handlers. No business logic belongs here.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes.tracking import router as tracking_router

from app.api.v1.routes.detection import router as detection_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging

# Logging must be configured before anything else runs, so that even
# startup-time log messages (model loading, directory creation) use our
# consistent format.
setup_logging()
logger = get_logger(__name__)

settings = get_settings()
settings.ensure_directories_exist()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves annotated result images (and anything else in app/static) at
# http://.../static/<path>. Example: static_dir/results/abc123.jpg
# becomes reachable at /static/results/abc123.jpg.
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

app.include_router(detection_router, prefix=settings.api_v1_prefix)
app.include_router(tracking_router, prefix=settings.api_v1_prefix)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Translate our custom domain exceptions into JSON HTTP responses.

    This is the ONLY place in the entire codebase that converts an
    AppException into an HTTP status code + body — services and clients
    never construct HTTP responses themselves.
    """
    logger.warning("Handled application exception: %s", exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for genuinely unexpected errors (bugs).

    Logs the full traceback for debugging, but never leaks internal
    details to the client — only a generic message.
    """
    logger.exception("Unhandled exception occurred.")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An unexpected internal error occurred."},
    )


@app.get("/health", tags=["Health"], summary="Basic health check")
async def health_check() -> dict:
    """Simple liveness check endpoint."""
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}