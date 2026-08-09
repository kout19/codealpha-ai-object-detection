"""Orchestrates the real-time detection-and-tracking pipeline.

Combines YOLOClient (detection), DeepSortTracker (tracking), and
VideoProcessor (frame I/O) into one per-frame pipeline:

    frame -> YOLOClient.predict -> raw detections
          -> DeepSortTracker.update -> tracked objects
          -> annotate frame
          -> encode as JPEG
          -> yield to the streaming endpoint

This is the only place these pieces are wired together — routes stay
thin, and each dependency (client/tracker/processor) stays independently
testable and reusable.
"""

import threading
import time
import uuid
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from fastapi import UploadFile

from app.clients.tracker import DeepSortTracker, RawDetection, TrackedObject
from app.clients.yolo_client import YOLOClient, get_yolo_client
from app.core.config import Settings, get_settings
from app.core.exceptions import (
    InvalidFileTypeError,
    TrackingAlreadyActiveError,
)
from app.core.logging import get_logger
from app.schemas.tracking import TrackingSourceType
from app.services.video_processor import VideoProcessor

logger = get_logger(__name__)

_ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
_BOX_COLOR = (46, 204, 113)   # BGR — green
_TEXT_COLOR = (255, 255, 255)


class TrackingService:
    """Owns and coordinates exactly one real-time tracking session at a time.

    Unlike DetectionService (stateless, safe to reconstruct per request),
    this class holds mutable session state — the open video source and the
    live tracker — that must be SHARED across /start, /stream, /stop, and
    /state calls. It is therefore used as a process-wide singleton (see
    get_tracking_service() below), not injected fresh per request.
    """

    def __init__(self, yolo_client: YOLOClient, settings: Settings) -> None:
        self._yolo_client = yolo_client
        self._settings = settings

        self._video_processor = VideoProcessor()
        self._tracker: DeepSortTracker | None = None

        self._lock = threading.Lock()
        self._is_tracking = False
        self._source_type: TrackingSourceType | None = None
        self._confidence: float | None = None

        self._latest_tracks: list[TrackedObject] = []
        self._last_frame_time: float | None = None
        self._fps: float = 0.0

    # --- Public control API -------------------------------------------------

    async def start(
        self,
        source: TrackingSourceType,
        webcam_index: int = 0,
        video_file: UploadFile | None = None,
        confidence: float | None = None,
    ) -> None:
        """Start a new tracking session.

        Args:
            source: Whether to read from a webcam or an uploaded video file.
            webcam_index: OS camera device index, used only when source is WEBCAM.
            video_file: The uploaded video, required when source is VIDEO_FILE.
            confidence: Optional confidence threshold override for this session.

        Raises:
            TrackingAlreadyActiveError: If a session is already running.
            InvalidFileTypeError: If the uploaded video has a disallowed extension.
            VideoSourceError: If the webcam/video file cannot be opened.
        """
        with self._lock:
            if self._is_tracking:
                raise TrackingAlreadyActiveError()

        if source == TrackingSourceType.WEBCAM:
            self._video_processor.open_webcam(webcam_index)
        else:
            video_path = await self._save_uploaded_video(video_file)
            self._video_processor.open_video_file(str(video_path))

        with self._lock:
            self._tracker = DeepSortTracker()
            self._source_type = source
            self._confidence = confidence
            self._latest_tracks = []
            self._last_frame_time = None
            self._fps = 0.0
            self._is_tracking = True

        logger.info("Tracking started (source=%s).", source.value)

    def stop(self) -> None:
        """Stop the current tracking session and release all resources."""
        with self._lock:
            self._is_tracking = False
            self._tracker = None
            self._latest_tracks = []

        self._video_processor.release()
        logger.info("Tracking stopped.")

    # --- Public query API -----------------------------------------------------

    def get_status(self) -> dict:
        """Return a snapshot of the current tracking status."""
        with self._lock:
            return {
                "tracking": self._is_tracking,
                "source": self._source_type.value if self._source_type else None,
                "active_objects": len(self._latest_tracks),
                "fps": round(self._fps, 1) if self._is_tracking else None,
            }

    def get_active_tracks(self) -> list[TrackedObject]:
        """Return the most recently computed set of tracked objects."""
        with self._lock:
            return list(self._latest_tracks)

    # --- Streaming generator ---------------------------------------------------

    def frame_generator(self):
        """Yield MJPEG-encoded annotated frames while tracking is active.

        Consumed directly by the /tracking/stream route via StreamingResponse.
        Each iteration performs: read frame -> YOLO detect -> Deep SORT
        update -> annotate -> JPEG encode -> yield.
        """
        while True:
            with self._lock:
                if not self._is_tracking:
                    break
                tracker = self._tracker
                confidence = self._confidence

            frame = self._video_processor.read_frame()
            if frame is None:
                logger.info("End of stream or unreadable frame; stopping tracking.")
                self.stop()
                break

            tracked_objects = self._process_frame(frame, tracker, confidence)
            annotated = self._annotate_frame(frame, tracked_objects)
            jpeg_bytes = self._video_processor.encode_jpeg(annotated)

            with self._lock:
                self._latest_tracks = tracked_objects
                self._update_fps()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n"
            )

    # --- Internal helpers --------------------------------------------------

    def _process_frame(
        self,
        frame: np.ndarray,
        tracker: DeepSortTracker,
        confidence: float | None,
    ) -> list[TrackedObject]:
        """Run YOLO detection, then Deep SORT tracking, on one frame."""
        effective_confidence = (
            confidence
            if confidence is not None
            else self._settings.model_confidence_threshold
        )
        results = self._yolo_client.predict(image=frame, confidence=effective_confidence)

        raw_detections: list[RawDetection] = []
        if results.boxes is not None:
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                raw_detections.append(
                    RawDetection(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        confidence=float(box.conf[0]),
                        label=results.names.get(class_id, str(class_id)),
                    )
                )

        return tracker.update(raw_detections, frame=frame)

    def _annotate_frame(
        self, frame: np.ndarray, tracked_objects: list[TrackedObject]
    ) -> np.ndarray:
        """Draw bounding boxes, labels, and track IDs onto a copy of the frame."""
        annotated = frame.copy()
        for obj in tracked_objects:
            cv2.rectangle(annotated, (obj.x1, obj.y1), (obj.x2, obj.y2), _BOX_COLOR, 2)

            caption = f"{obj.label} #{obj.track_id} {obj.confidence:.2f}"
            (text_w, text_h), _ = cv2.getTextSize(caption, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            cv2.rectangle(
                annotated,
                (obj.x1, max(0, obj.y1 - text_h - 8)),
                (obj.x1 + text_w + 6, obj.y1),
                _BOX_COLOR,
                -1,
            )
            cv2.putText(
                annotated,
                caption,
                (obj.x1 + 3, obj.y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                _TEXT_COLOR,
                1,
                cv2.LINE_AA,
            )
        return annotated

    def _update_fps(self) -> None:
        """Update a smoothed rolling FPS estimate from frame-to-frame timing."""
        now = time.monotonic()
        if self._last_frame_time is not None:
            delta = now - self._last_frame_time
            if delta > 0:
                instantaneous_fps = 1.0 / delta
                self._fps = (
                    instantaneous_fps
                    if self._fps == 0.0
                    else 0.9 * self._fps + 0.1 * instantaneous_fps  # EMA smoothing
                )
        self._last_frame_time = now

    async def _save_uploaded_video(self, video_file: UploadFile | None) -> Path:
        """Validate and persist an uploaded video to disk.

        Raises:
            InvalidFileTypeError: If no file was given or the extension
                isn't in the allowed set, or the file exceeds the
                configured video size limit.
        """
        if video_file is None or not video_file.filename:
            raise InvalidFileTypeError("A video file is required for the 'video_file' source.")

        extension = Path(video_file.filename).suffix.lower()
        if extension not in _ALLOWED_VIDEO_EXTENSIONS:
            raise InvalidFileTypeError(
                f"Video type '{extension}' is not supported. "
                f"Allowed types: {sorted(_ALLOWED_VIDEO_EXTENSIONS)}"
            )

        raw_bytes = await video_file.read()
        if len(raw_bytes) > self._settings.max_video_upload_size_bytes:
            raise InvalidFileTypeError(
                "Video exceeds the maximum allowed size of "
                f"{self._settings.max_video_upload_size_mb}MB."
            )

        filename = f"{uuid.uuid4().hex}{extension}"
        destination = self._settings.upload_dir / filename
        destination.write_bytes(raw_bytes)

        logger.info("Uploaded video saved to '%s'.", destination)
        return destination


# --- Dependency injection -----------------------------------------------------


@lru_cache
def get_tracking_service() -> TrackingService:
    """Return the process-wide singleton TrackingService.

    Must be a true singleton (not reconstructed per request, unlike
    DetectionService) because tracking session state — the open video
    source and the live tracker — has to persist and be shared across
    the separate /start, /stream, /stop, and /state HTTP calls.
    """
    return TrackingService(yolo_client=get_yolo_client(), settings=get_settings())