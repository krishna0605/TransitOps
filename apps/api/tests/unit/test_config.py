import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_debug_mode() -> None:
    with pytest.raises(ValidationError, match="DEBUG must be false"):
        Settings(app_env="production", debug=True)


def test_production_rejects_development_secret() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY must be changed"):
        Settings(app_env="production", debug=False)
