from kcrud.adapters.context import set_tenant_uri
from kcrud.infrastructure.config import AppConfig


async def apply_tenant_uri(config: AppConfig, uri: str | None) -> None:
    if not config.adapters.multitenant:
        return
    if not uri:
        raise ValueError("Mode multitenant : URI manquante dans la requête")
    set_tenant_uri(uri)
