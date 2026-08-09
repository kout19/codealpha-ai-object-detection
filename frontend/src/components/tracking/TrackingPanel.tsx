import { useState } from "react";
import { useTracking } from "@/hooks/useTracking";
import { ModeSelector } from "@/components/tracking/ModelSelector";
import { WebcamPanel } from "@/components/tracking/WebcamPanel";
import { VideoUploader } from "@/components/tracking/VideoUploader";
import { TrackingViewer } from "@/components/tracking/TrackingViewer";
import { TrackingControls } from "@/components/tracking/TrackingControl";
import { TrackingStatusBadge } from "@/components/tracking/TrackingStatusBadge";
import { DetectionStats } from "@/components/tracking/DetectionStats";
import { TrackedObjectsList } from "@/components/tracking/TrackingObjectsList";
import { ErrorMessage } from "@/components/ErrorMessage";

export function TrackingPanel() {
  const {
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
  } = useTracking();

  const [validationError, setValidationError] = useState<string | null>(null);

  const isBusy = status === "starting" || status === "tracking" || status === "stopping";
  const canStart = mode === "webcam" || selectedVideo !== null;
  const displayError = error ?? validationError;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <ModeSelector
          mode={mode}
          onChange={(newMode) => {
            setMode(newMode);
            setValidationError(null);
          }}
          disabled={isBusy}
        />
        <TrackingStatusBadge status={status} />
      </div>

      {displayError && <ErrorMessage message={displayError} />}

      {mode === "webcam" ? (
        <WebcamPanel
          webcamIndex={webcamIndex}
          onWebcamIndexChange={setWebcamIndex}
          disabled={isBusy}
        />
      ) : (
        <VideoUploader
          selectedFile={selectedVideo}
          onFileSelected={(file) => {
            setValidationError(null);
            setSelectedVideo(file);
          }}
          onValidationError={setValidationError}
          disabled={isBusy}
        />
      )}

      <TrackingViewer
        streamUrl={streamUrl}
        isStarting={status === "starting"}
        onStreamError={stop}
      />

      <TrackingControls status={status} canStart={canStart} onStart={start} onStop={stop} />

      <DetectionStats activeObjects={activeObjects} fps={fps} mode={mode} status={status} />

      {status === "tracking" && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-900">Tracked Objects</h3>
          <TrackedObjectsList tracks={tracks} />
        </div>
      )}
    </div>
  );
}