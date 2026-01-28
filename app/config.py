"""Configuration helpers for the Flask app."""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def _env_or_default(key: str, default: str) -> str:
    return os.environ.get(key, default)

def _env_bool(key: str, default: str) -> bool:
    return os.environ.get(key, default).lower() in {"1", "true", "yes"}

@dataclass

class AppConfig:
    DATABASE_URL: str = field(default_factory=lambda: _env_or_default(
        "DATABASE_URL", ""
    ))
    JWT_SECRET_KEY: str = field(default_factory=lambda: _env_or_default("JWT_SECRET_KEY", ""))
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = field(default_factory=lambda: int(_env_or_default("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "240")))
    DELIVERY_SOURCE_BRANCH_ID: str = field(default_factory=lambda: _env_or_default("DELIVERY_SOURCE_BRANCH_ID", ""))
    CORS_ALLOWED_ORIGINS: str = field(default_factory=lambda: _env_or_default("CORS_ALLOWED_ORIGINS", "*"))
    FRONTEND_BASE_URL: str = field(default_factory=lambda: _env_or_default("FRONTEND_BASE_URL", "http://localhost:5173"))
    BREVO_API_KEY: str = field(default_factory=lambda: _env_or_default("BREVO_API_KEY", ""))
    BREVO_RESET_TOKEN_OTP_ID: str = field(default_factory=lambda: _env_or_default("BREVO_RESET_TOKEN_OTP_ID", ""))
    BREVO_REGISTER_OTP_ID: str = field(default_factory=lambda: _env_or_default("BREVO_REGISTER_OTP_ID", ""))
    BREVO_SENDER_EMAIL: str = field(default_factory=lambda: _env_or_default("BREVO_SENDER_EMAIL", ""))
    ENABLE_REGISTRATION_OTP: bool = field(default_factory=lambda: _env_bool("ENABLE_REGISTRATION_OTP", "false"))
    APP_ENV: str = field(default_factory=lambda: _env_or_default("APP_ENV", "production"))
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = field(init=False)
    RATE_LIMIT_DEFAULTS: str = field(default_factory=lambda: _env_or_default("RATE_LIMIT_DEFAULTS", "200 per day, 50 per hour"))

    def __post_init__(self) -> None:
        self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
        self.validate()

    def validate(self) -> None:
        missing = []
        # Required in all environments
        if not self.DATABASE_URL:
            missing.append("DATABASE_URL")
        if not self.JWT_SECRET_KEY:
            missing.append("JWT_SECRET_KEY")
        # Required in production
        if self.APP_ENV == "production":
            if not self.BREVO_API_KEY:
                missing.append("BREVO_API_KEY")
            if not self.BREVO_SENDER_EMAIL:
                missing.append("BREVO_SENDER_EMAIL")
            if not self.DELIVERY_SOURCE_BRANCH_ID:
                missing.append("DELIVERY_SOURCE_BRANCH_ID")
            if self.CORS_ALLOWED_ORIGINS == "*":
                raise RuntimeError("CORS_ALLOWED_ORIGINS cannot be '*' in production")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
