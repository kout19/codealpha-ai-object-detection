/**
 * Dedicated API service for the tracking feature. No component should
 * call axios/fetch directly — everything routes through here, mirroring
 * the same pattern as detectObjects() in lib/api.ts.
 */

import axios from "axios";
import { API_BASE_URL, DetectionApiError, apiClient } from "@/apiAxios/api";
import type {
  TrackingStateResponse,
  TrackingStatusResponse,
} from "@/types/tracking";

const TRACKING_PREFIX = "/api/v1/tracking";

export async function startWebcamTracking(
  webcamIndex: number,
  confidence?: number,
): Promise<TrackingStatusResponse> {
  const formData = new FormData();
  formData.append("source", "webcam");
  formData.append("webcam_index", webcamIndex.toString());
  if (confidence !== undefined)
    formData.append("confidence", confidence.toString());
  return postStart(formData);
}

export async function startVideoTracking(
  file: File,
  confidence?: number,
): Promise<TrackingStatusResponse> {
  const formData = new FormData();
  formData.append("source", "video_file");
  formData.append("video", file);
  if (confidence !== undefined)
    formData.append("confidence", confidence.toString());
  return postStart(formData);
}

async function postStart(formData: FormData): Promise<TrackingStatusResponse> {
  try {
    const response = await apiClient.post<TrackingStatusResponse>(
      `${TRACKING_PREFIX}/start`,
      formData,
    );
    return response.data;
  } catch (error) {
    throw toTrackingApiError(error);
  }
}

export async function stopTracking(): Promise<TrackingStatusResponse> {
  try {
    const response = await apiClient.post<TrackingStatusResponse>(
      `${TRACKING_PREFIX}/stop`,
    );
    return response.data;
  } catch (error) {
    throw toTrackingApiError(error);
  }
}

export async function getTrackingState(): Promise<TrackingStateResponse> {
  try {
    const response = await apiClient.get<TrackingStateResponse>(
      `${TRACKING_PREFIX}/state`,
    );
    return response.data;
  } catch (error) {
    throw toTrackingApiError(error);
  }
}

/**
 * Builds the MJPEG stream URL for an <img> tag. `sessionKey` is a
 * cache-busting value that must change every time a new session starts —
 * an <img> won't reopen a fresh HTTP connection for a URL it already
 * loaded, even after the backend session behind it has restarted.
 */
export function getStreamUrl(sessionKey: number): string {
  return `${API_BASE_URL}${TRACKING_PREFIX}/stream?session=${sessionKey}`;
}

function toTrackingApiError(error: unknown): DetectionApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const backendMessage = (
      error.response?.data as { message?: string } | undefined
    )?.message;

    if (status === 409) {
      return new DetectionApiError(
        backendMessage ??
          "A tracking session is already active. Stop it first.",
        status,
      );
    }
    if (status === 400) {
      return new DetectionApiError(
        backendMessage ?? "Invalid tracking request.",
        status,
      );
    }
    if (status !== undefined && status >= 500) {
      return new DetectionApiError(
        backendMessage ?? "The server failed to process the tracking request.",
        status,
      );
    }
    if (!error.response) {
      return new DetectionApiError(
        "Could not reach the backend. Please check that the server is running.",
      );
    }
    return new DetectionApiError(
      backendMessage ?? "Something went wrong.",
      status,
    );
  }
  return new DetectionApiError("An unexpected error occurred.");
}
