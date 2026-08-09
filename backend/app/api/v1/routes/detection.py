"""API route for the object detection endpoint.

This router is intentionally thin: it only handles HTTP concerns (request
parsing, dependency injection, response status codes). All actual logic
lives in DetectionService. No YOLO logic, no file I/O logic, and no
business-rule validation belongs here — confidence range validation is
handled declaratively via FastAPI's Form(ge=..., le=...) constraints below.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.logging import get_logger
from app.schemas.detection import DetectionResponse
from app.services.detection_service import DetectionService, get_detection_service

logger = get_logger(__name__)

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post(
    "",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Run YOLO object detection on an uploaded image",
)
async def detect_objects(
    image: Annotated[
        UploadFile, File(description="Image file to run detection on.")
    ],
    confidence: Annotated[
        float | None,
        Form(
            description="Optional confidence threshold override (0.05-1.0). "
            "Omit to use the server default.",
            ge=0.05,
            le=1.0,
        ),
    ] = None,
    service: Annotated[DetectionService, Depends(get_detection_service)] = None,
) -> DetectionResponse:
    """Detect objects in an uploaded image using YOLOv8.

    Args:
        image: The uploaded image file (multipart/form-data).
        confidence: Optional per-request confidence threshold override.
            FastAPI rejects any value outside [0.05, 1.0] automatically
            with a 422 response, before this function body even runs.
        service: Injected DetectionService handling the actual pipeline.

    Returns:
        A DetectionResponse containing the annotated image URL and the
        list of detected objects.
    """
    logger.info(
        "Received detection request for file '%s' (confidence override=%s).",
        image.filename,
        confidence,
    )
    return await service.detect_objects(file=image, confidence=confidence)