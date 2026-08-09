"""Handles raw video I/O: opening a source, reading frames, releasing
resources, and encoding frames as JPEG for streaming.

This module has ONE job: talk to OpenCV's VideoCapture. It knows nothing
about YOLO or tracking — same separation of concerns as yolo_client.py
and tracker.py.
"""

import cv2
import numpy as np

from app.core.exceptions import VideoSourceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class VideoProcessor:
    """Wraps a single OpenCV VideoCapture source and its lifecycle."""

    def __init__(self) -> None:
        self._capture: cv2.VideoCapture | None = None

    def open_webcam(self, device_index: int = 0) -> None:
        """Open a local webcam device.

        Args:
            device_index: OS camera device index (0 is usually the default
                built-in camera).

        Raises:
            VideoSourceError: If the webcam cannot be opened.
        """
        self._capture = cv2.VideoCapture(device_index)
        if not self._capture.isOpened():
            raise VideoSourceError(
                f"Could not open webcam at index {device_index}. "
                "Check that a camera is connected and not already in use."
            )
        logger.info("Webcam opened (device index=%d).", device_index)

    def open_video_file(self, path: str) -> None:
        """Open a video file from disk.

        Args:
            path: Absolute path to the video file.

        Raises:
            VideoSourceError: If the file cannot be opened.
        """
        self._capture = cv2.VideoCapture(path)
        if not self._capture.isOpened():
            raise VideoSourceError(f"Could not open video file: {path}")
        logger.info("Video file opened: %s", path)

    def read_frame(self) -> np.ndarray | None:
        """Read the next available frame.

        Returns:
            The frame as a BGR NumPy array, or None if the source hasn't
            been opened, the stream ended, or a frame couldn't be read
            (e.g. end of video file, or webcam disconnected).
        """
        if self._capture is None:
            return None

        success, frame = self._capture.read()
        return frame if success else None

    def release(self) -> None:
        """Release the underlying VideoCapture resource.

        MUST be called whenever tracking stops or fails, to avoid leaking
        the OS-level camera handle or file descriptor.
        """
        if self._capture is not None:
            self._capture.release()
            self._capture = None
            logger.info("Video source released.")

    @property
    def is_open(self) -> bool:
        """Whether a video source is currently open and readable."""
        return self._capture is not None and self._capture.isOpened()

    @staticmethod
    def encode_jpeg(frame: np.ndarray) -> bytes:
        """Encode a frame as JPEG bytes for MJPEG streaming.

        Raises:
            VideoSourceError: If encoding fails.
        """
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            raise VideoSourceError("Failed to encode frame as JPEG.")
        return buffer.tobytes()