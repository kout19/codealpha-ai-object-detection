/**
 * Mirrors the backend's Pydantic schemas exactly (app/schemas/detection.py).
 * Keeping these in sync manually is fine at this project's scale.
 */

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  label: string;
  confidence: number;
  box: BoundingBox;
}

export interface DetectionResponse {
  success: boolean;
  message: string;
  image_url: string;
  detections: Detection[];
  count: number;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
}
