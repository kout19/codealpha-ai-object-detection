import { useCallback, useEffect, useRef, useState } from "react";
import {
  getStreamUrl,
  getTrackingState,
  startVideoTracking,
  startWebcamTracking,
  stopTracking as stopTrackingRequest,
} from "@/services/trackingApi";
import { DetectionApiError } from "@/apiAxios/api";
import type {
  TrackedObject,
  TrackingSourceType,
  TrackingUIStatus,
} from "@/types/tracking";

const POLL_INTERVAL_MS = 500;

export function useTracking() {
  const [status, setStatus] = useState<TrackingUIStatus>("idle");
  const [mode, setMode] = useState<TrackingSourceType>("webcam");
  const [webcamIndex, setWebcamIndex] = useState(0);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tracks, setTracks] = useState<TrackedObject[]>([]);
  const [activeObjects, setActiveObjects] = useState(0);
  const [fps, setFps] = useState<number | null>(null);
  const [sessionKey, setSessionKey] = useState(0);

  const pollRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback(() => {
    stopPolling();
    pollRef.current = window.setInterval(async () => {
      try {
        const state = await getTrackingState();
        setTracks(state.tracks);
        setActiveObjects(state.active_objects);
        setFps(state.fps);

        // Backend can stop itself (e.g. a video file reaching its end).
        if (!state.tracking) {
          stopPolling();
          setStatus("idle");
        }
      } catch {
        // A single transient poll failure shouldn't tear down a healthy
        // stream — the next tick will simply retry.
      }
    }, POLL_INTERVAL_MS);
  }, [stopPolling]);

  const start = useCallback(async () => {
    if (status === "starting" || status === "tracking") return;

    setStatus("starting");
    setError(null);

    try {
      if (mode === "webcam") {
        await startWebcamTracking(webcamIndex);
      } else {
        if (!selectedVideo) {
          throw new DetectionApiError("Please select a video file first.");
        }
        await startVideoTracking(selectedVideo);
      }

      setSessionKey((key) => key + 1);
      setStatus("tracking");
      startPolling();
    } catch (err) {
      const message =
        err instanceof DetectionApiError
          ? err.message
          : "Failed to start tracking. Please try again.";
      setError(message);
      setStatus("error");
    }
  }, [mode, webcamIndex, selectedVideo, status, startPolling]);

  const stop = useCallback(async () => {
    setStatus("stopping");
    stopPolling();

    try {
      await stopTrackingRequest();
    } catch (err) {
      const message =
        err instanceof DetectionApiError
          ? err.message
          : "Failed to stop tracking cleanly.";
      setError(message);
    } finally {
      setStatus("idle");
      setTracks([]);
      setActiveObjects(0);
      setFps(null);
    }
  }, [stopPolling]);

  const reset = useCallback(() => {
    stopPolling();
    setStatus("idle");
    setError(null);
    setTracks([]);
    setActiveObjects(0);
    setFps(null);
    setSelectedVideo(null);
  }, [stopPolling]);

  useEffect(() => stopPolling, [stopPolling]); // release the poll interval on unmount

  const streamUrl = status === "tracking" ? getStreamUrl(sessionKey) : null;

  return {
    status,
    mode,
    setMode,
    webcamIndex,
    setWebcamIndex,
    selectedVideo,
    setSelectedVideo,
    error,
    tracks,
    activeObjects,
    fps,
    streamUrl,
    start,
    stop,
    reset,
  };
}
