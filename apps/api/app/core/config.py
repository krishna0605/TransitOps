from functools import lru_cache
from typing import Literal, Self

from pydantic import AnyHttpUrl, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "TransitOps"
    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.1.0"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://transitops:transitops@localhost:5432/transitops"
    database_check_on_startup: bool = False

    jwt_secret_key: SecretStr = SecretStr("development-only-secret-change-before-production")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=15, gt=0)
    refresh_token_days: int = Field(default=7, gt=0)
    refresh_cookie_name: str = "transitops_refresh"

    redis_url: str = "redis://localhost:6379/0"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "transitops"
    s3_secret_key: SecretStr = SecretStr("transitops-local-only")
    s3_bucket: str = "transitops"
    s3_region: str = "us-east-1"
    max_upload_bytes: int = Field(default=10_485_760, gt=0)

    cors_origins: list[AnyHttpUrl] = [AnyHttpUrl("http://localhost:3000")]
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @model_validator(mode="after")
    def validate_production_security(self) -> Self:
        if self.app_env == "production":
            if self.debug:
                raise ValueError("DEBUG must be false in production")
            if len(self.jwt_secret_key.get_secret_value()) < 32:
                raise ValueError("JWT_SECRET_KEY must contain at least 32 characters")
            if "development-only" in self.jwt_secret_key.get_secret_value():
                raise ValueError("JWT_SECRET_KEY must be changed in production")
            if self.s3_secret_key.get_secret_value() == "transitops-local-only":
                raise ValueError("S3_SECRET_KEY must be changed in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
