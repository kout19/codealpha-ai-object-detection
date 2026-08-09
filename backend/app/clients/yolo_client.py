"""Thin client wrapper around the Ultralytics YOLO model.

This module's ONLY responsibility is communicating with the YOLO model:
loading it once, and running inference. It knows nothing about file
uploads, HTTP, or response formatting — that belongs to the service layer.
"""

from functools import lru_cache

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from app.core.config import Settings, get_settings
from app.core.exceptions import InferenceError, ModelLoadError
from app.core.logging import get_logger

logger = get_logger(__name__)


class YOLOClient:
    """Wraps a loaded YOLO model and exposes a simple predict() method.

    The model is loaded exactly once, in __init__, and reused for every
    subsequent call to predict(). Loading a YOLO model involves reading
    weights from disk and initializing the underlying torch model — far
    too expensive to repeat per request.
    """

    def __init__(self, settings: Settings) -> None:
        """Load the YOLO model immediately upon construction.

        Args:
            settings: Application settings, used for model_path and
                model_device.

        Raises:
            ModelLoadError: If the model cannot be loaded from disk.
        """
        self._settings = settings
        self._model = self._load_model()

    def _load_model(self) -> YOLO:
        """Load the YOLO model weights from disk onto the configured device."""
        try:
            logger.info(
                "Loading YOLO model '%s' on device '%s'.",
                self._settings.model_path,
                self._settings.model_device,
            )
            model = YOLO(self._settings.model_path)
            model.to(self._settings.model_device)
            logger.info("YOLO model loaded successfully.")
            return model
        except Exception as exc:  # noqa: BLE001 - intentional: wrap ANY load failure
            logger.exception("Failed to load YOLO model.")
            raise ModelLoadError(
                f"Could not load model from '{self._settings.model_path}': {exc}"
            ) from exc

    def predict(self, image: np.ndarray, confidence: float | None = None) -> Results:
        """Run object detection inference on a single image.

        Args:
            image: The image as a BGR NumPy array (OpenCV format).
            confidence: Optional confidence threshold override. Falls back
                to `settings.model_confidence_threshold` if not provided.

        Returns:
            The Ultralytics `Results` object for this image, containing
            bounding boxes, class ids, and confidence scores.

        Raises:
            InferenceError: If prediction fails for any reason.
        """
        effective_confidence = (
            confidence
            if confidence is not None
            else self._settings.model_confidence_threshold
        )
        try:
            results = self._model.predict(
                source=image,
                conf=effective_confidence,
                device=self._settings.model_device,
                verbose=False,
            )
            return results[0]
        except Exception as exc:  # noqa: BLE001 - intentional: wrap ANY inference failure
            logger.exception("YOLO inference failed.")
            raise InferenceError(f"Inference failed: {exc}") from exc


@lru_cache
def get_yolo_client() -> YOLOClient:
    """Return a cached, singleton YOLOClient instance.

    Like `get_settings()`, this guarantees the (expensive) model load
    happens exactly once per process, and every request reuses the same
    loaded model via FastAPI dependency injection.
    """
    return YOLOClient(settings=get_settings())