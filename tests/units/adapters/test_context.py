from arclith.adapters.context import _tenant_uri, get_tenant_uri, set_tenant_uri


def test_default_is_none():
    assert get_tenant_uri() is None


def test_set_and_get():
    token = set_tenant_uri("mongodb://example.com")
    try:
        assert get_tenant_uri() == "mongodb://example.com"
    finally:
        _tenant_uri.reset(token)


def test_reset_restores_previous():
    token = set_tenant_uri("mongodb://first")
    try:
        token2 = set_tenant_uri("mongodb://second")
        try:
            assert get_tenant_uri() == "mongodb://second"
        finally:
            _tenant_uri.reset(token2)
        assert get_tenant_uri() == "mongodb://first"
    finally:
        _tenant_uri.reset(token)

