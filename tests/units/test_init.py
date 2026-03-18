import pytest

import arclith


def test_getattr_console_logger():
    cls = arclith.ConsoleLogger
    from arclith.adapters.output.console.logger import ConsoleLogger
    assert cls is ConsoleLogger


def test_getattr_unknown_raises():
    with pytest.raises(AttributeError):
        _ = arclith.NonExistentSymbol  # type: ignore[attr-defined]
