"""API routes for real-time object detection and tracking."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import StreamingResponse

from app.core.exceptions import TrackingNotActiveError
from app.core.logging import get_logger
from app.schemas.detection import BoundingBox
from app.schemas.tracking import (
    TrackedObjectSchema,
    TrackingSourceType,
    TrackingStateResponse,
    TrackingStatusResponse,
)
from app.services.tracking_service import TrackingService, get_tracking_service

logger = get_logger(__name__)

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/start", response_model=TrackingStatusResponse, status_code=status.HTTP_200_OK)
async def start_tracking(
    source: Annotated[TrackingSourceType, Form(description="'webcam' or 'video_file'.")],
    webcam_index: Annotated[int, Form(description="Camera device index.")] = 0,
    confidence: Annotated[
        float | None,
        Form(description="Optional confidence override (0.05-1.0).", ge=0.05, le=1.0),
    ] = None,
    video: Annotated[
        UploadFile | None, File(description="Required when source='video_file'.")
    ] = None,
    service: Annotated[TrackingService, Depends(get_tracking_service)] = None,
) -> TrackingStatusResponse:
    """Start a real-time detection-and-tracking session."""
    await service.start(
        source=source, webcam_index=webcam_index, video_file=video, confidence=confidence
    )
    logger.info("Tracking session started via API (source=%s).", source.value)
    return TrackingStatusResponse(**service.get_status())


@router.get("/stream")
async def stream_tracking(
    service: Annotated[TrackingService, Depends(get_tracking_service)] = None,
) -> StreamingResponse:
    """Stream annotated, tracked frames as MJPEG.

    Point an <img src="..."> tag directly at this URL on the frontend.

    Raises:
        TrackingNotActiveError: If /tracking/start hasn't been called yet.
    """
    if not service.get_status()["tracking"]:
        raise TrackingNotActiveError("No tracking session is active. Call /tracking/start first.")

    return StreamingResponse(
        service.frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/stop", response_model=TrackingStatusResponse, status_code=status.HTTP_200_OK)
async def stop_tracking(
    service: Annotated[TrackingService, Depends(get_tracking_service)] = None,
) -> TrackingStatusResponse:
    """Stop the current tracking session and release resources."""
    service.stop()
    logger.info("Tracking session stopped via API.")
    return TrackingStatusResponse(**service.get_status())


@router.get("/state", response_model=TrackingStateResponse, status_code=status.HTTP_200_OK)
async def get_tracking_state(
    service: Annotated[TrackingService, Depends(get_tracking_service)] = None,
) -> TrackingStateResponse:
    """Poll tracking status and currently active tracked objects.

    Intended for the frontend sidebar (object count, IDs, labels,
    confidence) to poll every few hundred ms alongside the MJPEG stream.
    """
    status_snapshot = service.get_status()
    tracks = service.get_active_tracks()

    return TrackingStateResponse(
        tracking=status_snapshot["tracking"],
        active_objects=status_snapshot["active_objects"],
        fps=status_snapshot["fps"],
        tracks=[
            TrackedObjectSchema(
                track_id=t.track_id,
                label=t.label,
                confidence=t.confidence,
                box=BoundingBox(x1=t.x1, y1=t.y1, x2=t.x2, y2=t.y2),
            )
            for t in tracks
        ],
    )