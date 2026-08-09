import axios, { type AxiosError } from "axios";
import type { ApiErrorResponse, DetectionResponse } from "@/types/detection";

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

/**
 * Domain-specific error type for the frontend, mirroring the backend's
 * AppException pattern: a user-safe message plus an optional HTTP status,
 * so UI components never have to inspect raw Axios/HTTP internals.
 */
export class DetectionApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "DetectionApiError";
    this.status = status;
  }
}

/**
 * Sends an image to the backend's /api/v1/detect endpoint.
 *
 * IMPORTANT: We never set a Content-Type header manually. The browser
 * (via Axios) automatically sets `multipart/form-data; boundary=...`
 * when the body is a FormData instance. Setting it manually strips the
 * boundary and breaks the upload.
 */
export async function detectObjects(
  file: File,
  confidence?: number,
): Promise<DetectionResponse> {
  const formData = new FormData();
  formData.append("image", file);

  if (confidence !== undefined) {
    formData.append("confidence", confidence.toString());
  }

  try {
    const response = await apiClient.post<DetectionResponse>(
      "/api/v1/detect",
      formData,
    );
    return response.data;
  } catch (error) {
    throw toDetectionApiError(error);
  }
}

function toDetectionApiError(error: unknown): DetectionApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    if (axiosError.response) {
      const status = axiosError.response.status;
      const backendMessage = axiosError.response.data?.message;

      switch (status) {
        case 400:
          return new DetectionApiError(
            backendMessage ?? "The uploaded file could not be processed.",
            status,
          );
        case 413:
          return new DetectionApiError(
            backendMessage ?? "The image is too large.",
            status,
          );
        case 422:
          return new DetectionApiError(
            "Invalid request. Please check the image and try again.",
            status,
          );
        default:
          if (status >= 500) {
            return new DetectionApiError(
              backendMessage ??
                "The server encountered an error. Please try again.",
              status,
            );
          }
          return new DetectionApiError(
            backendMessage ?? "Something went wrong. Please try again.",
            status,
          );
      }
    }

    if (axiosError.request) {
      return new DetectionApiError(
        "Could not reach the server. Please check that the backend is running.",
      );
    }
  }

  return new DetectionApiError("An unexpected error occurred.");
}

/**
 * The backend returns a relative path like "/static/results/example.jpg".
 * This must be combined with the API base URL, not treated as a
 * frontend-relative route.
 */
export function getFullImageUrl(imageUrl: string): string {
  return `${API_BASE_URL}${imageUrl}`;
}
