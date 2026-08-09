"""Pydantic schemas for the real-time detection-and-tracking API."""

from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.detection import BoundingBox


class TrackingSourceType(str, Enum):
    """Where tracking frames come from."""

    WEBCAM = "webcam"
    VIDEO_FILE = "video_file"


class TrackedObjectSchema(BaseModel):
    """A single tracked object, exposed over the JSON polling endpoint."""

    track_id: int = Field(..., description="Persistent ID; stable across frames.")
    label: str = Field(..., description="Predicted class label.")
    confidence: float = Field(..., ge=0.0, le=1.0)
    box: BoundingBox


class TrackingStatusResponse(BaseModel):
    """Returned by /tracking/start and /tracking/stop."""

    tracking: bool
    source: str | None = None
    active_objects: int
    fps: float | None = None


class TrackingStateResponse(BaseModel):
    """Returned by GET /tracking/state for the live sidebar UI to poll."""

    tracking: bool
    active_objects: int
    fps: float | None = None
    tracks: list[TrackedObjectSchema]