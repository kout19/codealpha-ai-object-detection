"""Pydantic schemas for the object detection API.

These models define the exact shape of data crossing the API boundary:
what a client may send us, and what we guarantee to send back. FastAPI
uses these both for automatic request/response validation and for
generating the OpenAPI/Swagger documentation.
"""

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Pixel coordinates of a detected object's bounding box.

    Attributes:
        x1: Left edge x-coordinate.
        y1: Top edge y-coordinate.
        x2: Right edge x-coordinate.
        y2: Bottom edge y-coordinate.
    """

    x1: int = Field(..., description="Left edge x-coordinate, in pixels.")
    y1: int = Field(..., description="Top edge y-coordinate, in pixels.")
    x2: int = Field(..., description="Right edge x-coordinate, in pixels.")
    y2: int = Field(..., description="Bottom edge y-coordinate, in pixels.")


class Detection(BaseModel):
    """A single detected object.

    Attributes:
        label: The predicted class name (e.g. "person", "car").
        confidence: Model confidence score for this detection, in [0.0, 1.0].
        box: The bounding box surrounding the detected object.
    """

    label: str = Field(..., description="Predicted class label.")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0 and 1."
    )
    box: BoundingBox


class DetectionResponse(BaseModel):
    """Response returned by the /detect endpoint.

    Attributes:
        success: Whether detection completed successfully.
        message: Human-readable status message.
        image_url: Relative URL to the annotated result image, served
            via the mounted /static route.
        detections: List of all objects detected in the image.
        count: Total number of objects detected (redundant with
            len(detections), but convenient for clients to avoid counting).
    """

    success: bool
    message: str
    image_url: str
    detections: list[Detection]
    count: int