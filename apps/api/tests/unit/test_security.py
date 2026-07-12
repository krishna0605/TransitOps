from uuid import uuid4

from app.core.config import Settings
from app.core.security import (
    AccessClaims,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_round_trip() -> None:
    encoded = hash_password("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("incorrect", encoded)


def test_access_token_round_trip() -> None:
    settings = Settings(app_env="test", debug=False)
    claims = AccessClaims(
        user_id=uuid4(),
        organization_id=uuid4(),
        membership_id=uuid4(),
        role="Dispatcher",
        session_id=uuid4(),
    )
    token, expires_at = create_access_token(settings, claims)
    assert expires_at.tzinfo is not None
    assert decode_access_token(settings, token) == claims
