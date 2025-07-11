from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator  # type: ignore

from .api.routes import router as api_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="Financial Intelligence RAG API",
        version="0.1.0",
    )

    # CORS configuration (allow all for development)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 