from kcrud.adapters.context import set_tenant_uri
from kcrud.infrastructure.config import AppConfig


class MissingTenantURIError(Exception):
    """Raised in multitenant mode when the tenant URI is missing from the request."""


async def apply_tenant_uri(config: AppConfig, uri: str | None) -> None:
    if not config.adapters.multitenant:
        return
    if not uri:
        raise MissingTenantURIError(
            "Mode multitenant : URI manquante dans la requête"
        )
    set_tenant_uri(uri)
