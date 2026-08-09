"""Business logic for the object detection feature.

This is the orchestration layer: it validates uploads, coordinates the
YOLOClient, draws/saves the annotated result image, and assembles the
final response schema. Routers stay thin; YOLOClient stays a pure model
wrapper; all "what actually happens on a detection request" logic lives
here.
"""

import uuid
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from fastapi import Depends, UploadFile

from app.clients.yolo_client import YOLOClient, get_yolo_client
from app.core.config import Settings, get_settings
from app.core.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileTypeError,
    InvalidImageError,
)
from app.core.logging import get_logger
from app.schemas.detection import BoundingBox, Detection, DetectionResponse

logger = get_logger(__name__)





#last code
class DetectionService:
    """Coordinates upload validation, inference, and response assembly."""

    def __init__(self, yolo_client: YOLOClient, settings: Settings) -> None:
        """Initialize the service with its dependencies.

        Args:
            yolo_client: The YOLO model wrapper used to run inference.
            settings: Application settings for validation limits and paths.
        """
        self._yolo_client = yolo_client
        self._settings = settings

    async def detect_objects(
        self, file: UploadFile, confidence: float | None = None
    ) -> DetectionResponse:
        """Run the full detection pipeline on an uploaded image.

        Args:
            file: The uploaded image file.
            confidence: Optional confidence threshold override.

        Returns:
            A fully populated DetectionResponse.

        Raises:
            InvalidFileTypeError: If the file extension isn't allowed.
            EmptyFileError: If the file has zero bytes.
            FileTooLargeError: If the file exceeds the configured limit.
            InvalidImageError: If the file can't be decoded as an image.
            InferenceError: If the YOLO model fails during prediction.
        """
        self._validate_extension(file.filename)

        raw_bytes = await file.read()
        self._validate_size(raw_bytes)

        image = self._decode_image(raw_bytes)
        effective_confidence=self._resolve_concidence(confidence)

        results = self._yolo_client.predict(image=image, confidence=confidence)
        detections = self._extract_detections(results)
        annotated_filename = self._save_annotated_image(results)

        logger.info(
            "Detection completed for '%s': %d object(s) found.",
            file.filename,
            len(detections),
        )

        return DetectionResponse(
            success=True,
            message="Object detection completed successfully.",
            image_url=f"/static/results/{annotated_filename}",
            detections=detections,
            count=len(detections),
        )
    def _resolve_concidence(self, confidence: float | None) -> float:
        return(
            confidence
            if confidence is not None
            else self._settings.model_confidence_threshold  
        )
    def _validate_extension(self, filename: str | None) -> None:
        """Reject files with a missing or disallowed extension."""
        if not filename:
            raise InvalidFileTypeError("Uploaded file has no filename.")

        extension = Path(filename).suffix.lower()
        if extension not in self._settings.allowed_image_extensions:
            allowed = sorted(self._settings.allowed_image_extensions)
            raise InvalidFileTypeError(
                f"File type '{extension}' is not supported. Allowed types: {allowed}"
            )

    def _validate_size(self, raw_bytes: bytes) -> None:
        """Reject empty files and files exceeding the configured size limit."""
        if len(raw_bytes) == 0:
            raise EmptyFileError()

        if len(raw_bytes) > self._settings.max_upload_size_bytes:
            raise FileTooLargeError(
                "File exceeds the maximum allowed size of "
                f"{self._settings.max_upload_size_mb}MB."
            )

    def _decode_image(self, raw_bytes: bytes) -> np.ndarray:
        """Decode raw uploaded bytes into an OpenCV BGR image array."""
        np_buffer = np.frombuffer(raw_bytes, dtype=np.uint8)
        image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

        if image is None:
            raise InvalidImageError(
                "Uploaded file could not be decoded as a valid image."
            )
        return image

    def _extract_detections(self, results) -> list[Detection]:
        """Convert raw Ultralytics results into our Detection schema list."""
        detections: list[Detection] = []
        boxes = results.boxes

        if boxes is None:
            return detections

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence_score = float(box.conf[0])
            class_id = int(box.cls[0])
            label = results.names.get(class_id, str(class_id))

            detections.append(
                Detection(
                    label=label,
                    confidence=round(confidence_score, 4),
                    box=BoundingBox(
                        x1=round(x1), y1=round(y1), x2=round(x2), y2=round(y2)
                    ),
                )
            )
        return detections

    def _save_annotated_image(self, results) -> str:
        """Render bounding boxes onto the image and save it to disk.

        Returns:
            The generated filename (not full path) of the saved image.
        """
        annotated_array = results.plot()  # BGR NumPy array with boxes drawn

        filename = f"{uuid.uuid4().hex}.jpg"
        output_path = self._settings.results_dir / filename

        cv2.imwrite(str(output_path), annotated_array)
        return filename


@lru_cache
def get_detection_service_singleton() -> DetectionService:
    """Internal singleton builder — do not call directly from routes."""
    return DetectionService(yolo_client=get_yolo_client(), settings=get_settings())


def get_detection_service(
    yolo_client: YOLOClient = Depends(get_yolo_client),
    settings: Settings = Depends(get_settings),
) -> DetectionService:
    """FastAPI dependency that provides a DetectionService instance.

    Declared with `Depends(...)` parameters (rather than just calling the
    singleton builder directly) so that tests can override `get_yolo_client`
    or `get_settings` via `app.dependency_overrides` and have those
    overrides correctly propagate into the service.
    """
    return DetectionService(yolo_client=yolo_client, settings=settings)