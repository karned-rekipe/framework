from contextvars import ContextVar, Token

from arclith.domain.models.tenant import AdapterTenantCoords, TenantContext

_tenant_context: ContextVar[TenantContext | None] = ContextVar("tenant_context", default=None)


def set_tenant_context(ctx: TenantContext) -> Token:
    return _tenant_context.set(ctx)


def get_tenant_context() -> TenantContext | None:
    return _tenant_context.get()


def get_adapter_tenant_context(adapter: str) -> AdapterTenantCoords | None:
    """Retourne les coordonnées du tenant pour un adaptateur donné, ou None."""
    ctx = _tenant_context.get()
    return ctx.get(adapter) if ctx else None


# Backward-compat shims — prefer get_adapter_tenant_context / set_tenant_context
def set_tenant_uri(uri: str) -> Token:
    return set_tenant_context(TenantContext(adapters={"mongodb": AdapterTenantCoords(params={"uri": uri})}))


def get_tenant_uri() -> str | None:
    coords = get_adapter_tenant_context("mongodb")
    return coords.get("uri") if coords else None
