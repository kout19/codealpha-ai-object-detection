"""Application configuration.

This module defines a single, centralized, typed configuration object for
the entire backend. All environment-dependent values (paths, model settings,
server settings, CORS, upload limits) must be declared here and nowhere else.

No other module in this application should call `os.environ` or `os.getenv`
directly — always go through `get_settings()`.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings.

    Values are loaded, in order of precedence, from:
        1. Environment variables (highest precedence).
        2. A `.env` file in the project root.
        3. The default values declared below (lowest precedence).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- General app metadata ---
    app_name: str = "AI Object Detection API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # --- CORS ---
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # --- YOLO model settings ---
    model_path: str = "yolov8n.pt"
    model_confidence_threshold: float = 0.25
    model_device: str = "cpu"

    # --- Filesystem paths ---
    base_dir: Path = Path(__file__).resolve().parent.parent
    upload_dir: Path = base_dir / "uploads"
    static_dir: Path = base_dir / "static"

    # --- Upload constraints ---
    max_upload_size_mb: int = 10
    allowed_image_extensions: set[str] = Field(
        default_factory=lambda: {".jpg", ".jpeg", ".png", ".webp"}
    )

    # --- Logging ---
    log_level: str = "INFO"

    @field_validator("model_confidence_threshold")
    @classmethod
    def validate_confidence_threshold(cls, value: float) -> float:
        """Ensure the confidence threshold is a valid probability."""
        if not 0.0 <= value <= 1.0:
            raise ValueError(
                "model_confidence_threshold must be between 0.0 and 1.0, "
                f"got {value}"
            )
        return value

    @field_validator("max_upload_size_mb")
    @classmethod
    def validate_max_upload_size(cls, value: int) -> int:
        """Ensure the max upload size is a sane positive number."""
        if value <= 0:
            raise ValueError(
                f"max_upload_size_mb must be a positive integer, got {value}"
            )
        return value

    @property
    def max_upload_size_bytes(self) -> int:
        """Convenience conversion of the MB limit to bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def results_dir(self) -> Path:
        """Directory where annotated detection result images are stored."""
        return self.static_dir / "results"

    def ensure_directories_exist(self) -> None:
        """Create upload/static/results directories on disk if missing."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return a cached, singleton instance of the application settings."""
    return Settings()