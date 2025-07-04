import uvicorn
from fastapi import FastAPI, Request
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.rate_limit import limiter
from app.api import admin as admin_router
from app.api import discord as discord_router
from app.api import inspector as inspector_router
from app.middleware.audit import AuditMiddleware

app = FastAPI(title=settings.app_name)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register middleware
app.add_middleware(AuditMiddleware)

# Routers
app.include_router(admin_router.router)
app.include_router(discord_router.router)
app.include_router(inspector_router.router)

@app.get("/health", tags=["Health"])
@limiter.limit("5/minute")
async def health_check(request: Request):
    """Simple health-check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 