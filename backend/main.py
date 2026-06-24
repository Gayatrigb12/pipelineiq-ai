from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialise resources (DB connections, model loading, etc.)
    yield
    # Shutdown: release resources


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG API",
        description="FastAPI + LangChain RAG application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],        # Restrict in production (e.g. env var)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------
    app.include_router(health_router)

    return app


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str


# ---------------------------------------------------------------------------
# Health router
# ---------------------------------------------------------------------------

from fastapi import APIRouter  # noqa: E402 (kept co-located for single-file clarity)

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    status_code=200,
)
async def health_check() -> HealthResponse:
    """Returns service health status."""
    return HealthResponse(status="healthy")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
    )