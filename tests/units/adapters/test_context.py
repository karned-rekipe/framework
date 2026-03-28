from arclith.adapters.context import (
    _tenant_context,
    get_adapter_tenant_context,
    get_tenant_uri,
    set_tenant_context,
    set_tenant_uri,
)
from arclith.domain.models.tenant import AdapterTenantCoords, TenantContext


def test_default_is_none():
    assert get_tenant_uri() is None


def test_set_and_get():
    token = set_tenant_uri("mongodb://example.com")
    try:
        assert get_tenant_uri() == "mongodb://example.com"
    finally:
        _tenant_context.reset(token)


def test_reset_restores_previous():
    token = set_tenant_uri("mongodb://first")
    try:
        token2 = set_tenant_uri("mongodb://second")
        try:
            assert get_tenant_uri() == "mongodb://second"
        finally:
            _tenant_context.reset(token2)
        assert get_tenant_uri() == "mongodb://first"
    finally:
        _tenant_context.reset(token)


def test_get_adapter_tenant_context_returns_coords():
    ctx = TenantContext(adapters={
        "mongodb": AdapterTenantCoords(params={"uri": "mongodb://tenant-a", "db_name": "db_a"}),
    })
    token = set_tenant_context(ctx)
    try:
        coords = get_adapter_tenant_context("mongodb")
        assert coords is not None
        assert coords.get("uri") == "mongodb://tenant-a"
        assert coords.get("db_name") == "db_a"
    finally:
        _tenant_context.reset(token)


def test_adapter_coords_require_raises_on_missing_key():
    coords = AdapterTenantCoords(params={"uri": "mongodb://tenant-a"})
    assert coords.get("db_name") is None
    try:
        coords.require("db_name")
        assert False, "Should have raised"
    except KeyError:
        pass


def test_get_adapter_tenant_context_unknown_adapter_returns_none():
    ctx = TenantContext(adapters={
        "mongodb": AdapterTenantCoords(params={"uri": "mongodb://tenant-a"}),
    })
    token = set_tenant_context(ctx)
    try:
        assert get_adapter_tenant_context("mariadb") is None
    finally:
        _tenant_context.reset(token)


def test_s3_adapter_coords():
    ctx = TenantContext(adapters={
        "s3": AdapterTenantCoords(params={
            "endpoint_url": "https://s3.eu-west-1.amazonaws.com",
            "bucket_name": "tenant-foo",
            "region": "eu-west-1",
        }),
    })
    token = set_tenant_context(ctx)
    try:
        coords = get_adapter_tenant_context("s3")
        assert coords is not None
        assert coords.require("bucket_name") == "tenant-foo"
        assert coords.get("region") == "eu-west-1"
    finally:
        _tenant_context.reset(token)


def test_mixed_mode_adapters_independent():
    """MongoDB multitenant + MariaDB single-tenant : seul mongodb est dans le context."""
    ctx = TenantContext(adapters={
        "mongodb": AdapterTenantCoords(params={"uri": "mongodb://tenant-a", "db_name": "db_a"}),
    })
    token = set_tenant_context(ctx)
    try:
        assert get_adapter_tenant_context("mongodb") is not None
        assert get_adapter_tenant_context("mariadb") is None
    finally:
        _tenant_context.reset(token)




