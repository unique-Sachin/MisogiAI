from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Initialise the Limiter with global default limits
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
) 