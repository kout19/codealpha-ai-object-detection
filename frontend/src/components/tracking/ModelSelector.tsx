import { Camera, FileVideo } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { TrackingSourceType } from "@/types/tracking";

interface ModeSelectorProps {
  mode: TrackingSourceType;
  onChange: (mode: TrackingSourceType) => void;
  disabled?: boolean;
}

export function ModeSelector({ mode, onChange, disabled }: ModeSelectorProps) {
  return (
    <div className="inline-flex rounded-lg border bg-white p-1">
      <Button
        type="button"
        size="sm"
        variant={mode === "webcam" ? "default" : "ghost"}
        onClick={() => onChange("webcam")}
        disabled={disabled}
      >
        <Camera className="mr-1.5 h-4 w-4" />
        Webcam
      </Button>
      <Button
        type="button"
        size="sm"
        variant={mode === "video_file" ? "default" : "ghost"}
        onClick={() => onChange("video_file")}
        disabled={disabled}
      >
        <FileVideo className="mr-1.5 h-4 w-4" />
        Video File
      </Button>
    </div>
  );
}
