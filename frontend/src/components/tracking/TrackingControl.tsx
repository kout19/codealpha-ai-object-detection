import { Play, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { TrackingUIStatus } from "@/types/tracking";

interface TrackingControlsProps {
  status: TrackingUIStatus;
  canStart: boolean;
  onStart: () => void;
  onStop: () => void;
}

export function TrackingControls({
  status,
  canStart,
  onStart,
  onStop,
}: TrackingControlsProps) {
  const isActive = status === "tracking" || status === "starting";

  return (
    <div className="flex justify-center gap-3">
      <Button onClick={onStart} disabled={isActive || !canStart} size="lg">
        <Play className="mr-1.5 h-4 w-4" />
        {status === "starting" ? "Starting…" : "Start Tracking"}
      </Button>
      <Button onClick={onStop} disabled={!isActive} variant="outline" size="lg">
        <Square className="mr-1.5 h-4 w-4" />
        Stop Tracking
      </Button>
    </div>
  );
}
