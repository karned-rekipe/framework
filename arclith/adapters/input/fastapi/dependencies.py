from collections.abc import Callable

from fastapi import Request

from arclith.adapters.input.dependencies import apply_tenant_uri
from arclith.infrastructure.config import AppConfig


def make_inject_tenant_uri(config: AppConfig) -> Callable:
    async def inject_tenant_uri(request: Request) -> None:
        # TODO: JWT → vault → URI
        await apply_tenant_uri(config, request.headers.get("X-Tenant-URI"))

    return inject_tenant_uri
