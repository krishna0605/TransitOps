import pytest
from pydantic import ValidationError

from app.contracts.idempotency import IdempotencyKey


@pytest.mark.parametrize("value", ["trip-1234", "request:123", "abc_def.123"])
def test_idempotency_key_accepts_supported_values(value: str) -> None:
    assert IdempotencyKey(value).root == value


@pytest.mark.parametrize("value", ["short", "contains spaces", "contains/slash"])
def test_idempotency_key_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValidationError):
        IdempotencyKey(value)
