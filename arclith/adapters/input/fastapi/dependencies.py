from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import Request

from arclith.adapters.input.dependencies import apply_tenant_uri
from arclith.infrastructure.config import AppConfig


def make_inject_tenant_uri(config: AppConfig) -> Callable:
    async def inject_tenant_uri(request: Request) -> None:
        # TODO: JWT → vault → URI
        await apply_tenant_uri(config, request.headers.get("X-Tenant-URI"))

    return inject_tenant_uri


async def get_duration_ms(request: Request) -> float:
    """FastAPI dependency — returns elapsed ms since request start.

    Requires ``TimingMiddleware`` to be active (injected by ``Arclith.fastapi()``).
    Returns 0.0 if middleware is absent.

    Usage::

        async def my_endpoint(duration_ms: Annotated[float, Depends(get_duration_ms)]):
            return success_response(data, metadata=ResponseMetadata(duration_ms=int(duration_ms)))
    """
    start: float | None = getattr(request.state, "start_time", None)
    if start is None:
        return 0.0
    return round((time.monotonic() - start) * 1000)
