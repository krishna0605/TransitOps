import re

from pydantic import RootModel, field_validator

IDEMPOTENCY_HEADER = "Idempotency-Key"
IDEMPOTENCY_KEY_PATTERN = re.compile(r"^[A-Za-z0-9._:-]+$")


class IdempotencyKey(RootModel[str]):
    @field_validator("root")
    @classmethod
    def validate_key(cls, value: str) -> str:
        key = value.strip()
        if not 8 <= len(key) <= 128:
            raise ValueError("idempotency key must contain 8 to 128 characters")
        if not IDEMPOTENCY_KEY_PATTERN.fullmatch(key):
            raise ValueError("idempotency key contains unsupported characters")
        return key
