import type { BoundingBox } from "@/types/detection";

export type TrackingSourceType = "webcam" | "video_file";

export interface TrackedObject {
  track_id: number;
  label: string;
  confidence: number;
  box: BoundingBox;
}

export interface TrackingStatusResponse {
  tracking: boolean;
  source: string | null;
  active_objects: number;
  fps: number | null;
}

export interface TrackingStateResponse {
  tracking: boolean;
  active_objects: number;
  fps: number | null;
  tracks: TrackedObject[];
}

/** Frontend-only UI state machine, layered on top of the backend's tracking boolean. */
export type TrackingUIStatus =
  | "idle"
  | "starting"
  | "tracking"
  | "stopping"
  | "error";
