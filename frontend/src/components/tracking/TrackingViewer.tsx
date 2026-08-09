import { Video, VideoOff } from "lucide-react";

interface TrackingViewerProps {
  streamUrl: string | null;
  isStarting: boolean;
  onStreamError: () => void;
}

export function TrackingViewer({
  streamUrl,
  isStarting,
  onStreamError,
}: TrackingViewerProps) {
  return (
    <div className="flex aspect-video w-full items-center justify-center overflow-hidden rounded-xl border bg-slate-950">
      {streamUrl ? (
        <img
          src={streamUrl}
          alt="Live tracking feed"
          className="h-full w-full object-contain"
          onError={onStreamError}
        />
      ) : (
        <div className="flex flex-col items-center gap-2 text-slate-500">
          {isStarting ? (
            <>
              <Video className="h-8 w-8 animate-pulse" />
              <p className="text-sm">Starting session…</p>
            </>
          ) : (
            <>
              <VideoOff className="h-8 w-8" />
              <p className="text-sm">No active stream</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
