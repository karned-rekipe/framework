from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request

from arclith.adapters.context import set_tenant_context
from arclith.domain.models.tenant import TenantContext
from arclith.infrastructure.config import AppConfig

if TYPE_CHECKING:
    from arclith.adapters.input.jwt.decoder import JWTDecoder
    from arclith.domain.ports.license_validator import LicenseValidator
    from arclith.domain.ports.tenant_resolver import TenantResolver


def make_inject_tenant_uri(
    config: AppConfig,
    *,
    jwt_decoder: "JWTDecoder | None" = None,
    license_validator: "LicenseValidator | None" = None,
    tenant_resolvers: "list[TenantResolver] | None" = None,
) -> Callable:
    """Retourne une dépendance FastAPI qui injecte le TenantContext pour la requête courante.

    En mode **single-tenant** (``config.adapters.multitenant`` est False), la dépendance
    est un no-op : les adapters utilisent directement leur config statique.

    En mode **multi-tenant**, le pipeline complet s'exécute :
    1. Extraction et validation du JWT (Keycloak JWKS, mis en cache)
    2. Vérification de la licence (realm role)
    3. Résolution parallèle de **tous** les resolvers tenant (un par adaptateur multitenant)
    4. Merge des TenantContexts → un seul TenantContext par requête

    ``tenant_resolvers`` est une **liste** — un resolver par adaptateur multitenant.
    Exemple : ``[VaultTenantResolver("mongodb", ...), VaultTenantResolver("s3_client", ...)]``
    Les adaptateurs non-multitenant (bucket applicatif partagé, etc.) ne sont pas listés ici.
    """

    async def inject_tenant_uri(request: Request) -> None:
        if not config.adapters.multitenant:
            return

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header manquant ou invalide")
        token = auth.removeprefix("Bearer ")

        if jwt_decoder is None:
            raise RuntimeError("jwt_decoder requis en mode multitenant")
        claims: dict = await jwt_decoder.decode(token)

        if license_validator is not None and not license_validator.validate(claims):
            raise HTTPException(status_code=403, detail="Licence invalide ou absente")

        tenant_claim = config.tenant.tenant_claim if config.tenant else "sub"
        tenant_id: str | None = claims.get(tenant_claim)
        if not tenant_id:
            raise HTTPException(status_code=401, detail=f"Claim '{tenant_claim}' absent du token")

        resolvers = tenant_resolvers or []
        if not resolvers:
            raise RuntimeError("tenant_resolvers requis en mode multitenant")

        # Résolution parallèle — un resolver par adaptateur multitenant
        results = await asyncio.gather(*[r.resolve(tenant_id) for r in resolvers])

        # Merge : tous les adapters dans un seul TenantContext
        merged = TenantContext(adapters={
            adapter: coords
            for ctx in results
            for adapter, coords in ctx.adapters.items()
        })
        set_tenant_context(merged)

    return inject_tenant_uri


async def get_duration_ms(request: Request) -> float:
    """FastAPI dependency — returns elapsed ms since request start.

    Requires ``TimingMiddleware`` to be active (injected by ``Arclith.fastapi()``).
    Returns 0.0 if middleware is absent.
    """
    start: float | None = getattr(request.state, "start_time", None)
    if start is None:
        return 0.0
    return round((time.monotonic() - start) * 1000)



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
