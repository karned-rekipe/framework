from collections.abc import Callable

import fastmcp

from arclith.adapters.input.dependencies import apply_tenant_uri
from arclith.infrastructure.config import AppConfig


def make_inject_tenant_uri(config: AppConfig) -> Callable:
    async def inject_tenant_uri(ctx: fastmcp.Context) -> None:
        # TODO: JWT → vault → URI
        try:
            uri = ctx.request_context.request.headers.get("x-tenant-uri")  # type: ignore[union-attr]
        except Exception:
            uri = None
        await apply_tenant_uri(config, uri)

    return inject_tenant_uri
