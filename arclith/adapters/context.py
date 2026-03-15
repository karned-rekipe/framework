from contextvars import ContextVar, Token

_tenant_uri: ContextVar[str | None] = ContextVar("tenant_uri", default = None)


def set_tenant_uri(uri: str) -> Token:
    return _tenant_uri.set(uri)


def get_tenant_uri() -> str | None:
    return _tenant_uri.get()
