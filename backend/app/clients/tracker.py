"""Thin client wrapper around the Deep SORT tracking algorithm.

This module's ONLY responsibility is talking to Deep SORT: feeding it
per-frame detections and reading back persistent tracked objects. It knows
nothing about video capture, YOLO, or frame annotation — same separation
of concerns as YOLOClient in this same package.
"""

from dataclasses import dataclass

import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RawDetection:
    """A single per-frame detection, as produced by YOLO.

    Attributes:
        x1, y1, x2, y2: Bounding box corners, in pixels.
        confidence: Detection confidence score.
        label: Predicted class label (e.g. "person").
    """

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    label: str


@dataclass
class TrackedObject:
    """A single tracked object with a persistent ID across frames.

    Attributes:
        track_id: Stable ID assigned by Deep SORT. Stays the same for the
            same physical object across frames — this is what distinguishes
            tracking from plain per-frame detection.
        label: Predicted class label.
        confidence: Most recent detection confidence for this track.
        x1, y1, x2, y2: Current bounding box corners, in pixels.
    """

    track_id: int
    label: str
    confidence: float
    x1: int
    y1: int
    x2: int
    y2: int


class DeepSortTracker:
    """Wraps one Deep SORT tracker instance for one tracking session.

    A single instance must be reused across every frame of a session —
    constructing a new one per frame would reset all track IDs, which
    defeats the entire point of tracking (see TrackingService, which owns
    exactly one instance of this class per active session).
    """

    def __init__(self, max_age: int = 30) -> None:
        """Initialize a fresh tracker.

        Args:
            max_age: Number of consecutive missed frames before a track is
                dropped. Higher values tolerate brief occlusions (an object
                walking behind another) at the cost of keeping stale tracks
                around longer.
        """
        self._tracker = DeepSort(max_age=max_age)
        self._max_age = max_age
        logger.info("Deep SORT tracker initialized (max_age=%d).", max_age)

    def update(
        self, detections: list[RawDetection], frame: np.ndarray
    ) -> list[TrackedObject]:
        """Update tracks with the current frame's detections.

        Args:
            detections: Objects YOLO found in this frame.
            frame: The current frame (BGR NumPy array). Deep SORT uses this
                internally for appearance-based re-identification.

        Returns:
            Currently confirmed tracked objects (unconfirmed/tentative
            tracks — usually a brand-new object seen for only 1-2 frames —
            are filtered out to avoid flickering IDs in the UI).
        """
        raw_input = [
            (
                [det.x1, det.y1, det.x2 - det.x1, det.y2 - det.y1],  # [left, top, w, h]
                det.confidence,
                det.label,
            )
            for det in detections
        ]

        tracks = self._tracker.update_tracks(raw_input, frame=frame)

        tracked_objects: list[TrackedObject] = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            left, top, right, bottom = track.to_ltrb()
            tracked_objects.append(
                TrackedObject(
                    track_id=int(track.track_id),
                    label=track.get_det_class() or "object",
                    confidence=float(track.get_det_conf() or 0.0),
                    x1=int(left),
                    y1=int(top),
                    x2=int(right),
                    y2=int(bottom),
                )
            )
        return tracked_objects

    def reset(self) -> None:
        """Discard all current tracks, e.g. when starting a fresh session."""
        self._tracker = DeepSort(max_age=self._max_age)
        logger.info("Deep SORT tracker reset.")