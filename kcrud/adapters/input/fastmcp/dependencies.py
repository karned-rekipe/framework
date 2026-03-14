from collections.abc import Callable

import fastmcp

from kcrud.adapters.input.dependencies import apply_tenant_uri
from kcrud.infrastructure.config import AppConfig


def make_inject_tenant_uri(config: AppConfig) -> Callable:
    async def inject_tenant_uri(ctx: fastmcp.Context) -> None:
        # TODO: JWT → vault → URI
        try:
            uri = ctx.request_context.request.headers.get("x-tenant-uri")
        except Exception:
            uri = None
        await apply_tenant_uri(config, uri)

    return inject_tenant_uri
