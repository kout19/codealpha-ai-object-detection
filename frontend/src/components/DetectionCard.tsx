import { Badge } from "@/components/ui/badge";
import type { Detection } from "@/types/detection";

interface DetectionCardProps {
  detection: Detection;
  index: number;
}

function confidenceVariant(
  confidence: number,
): "default" | "secondary" | "outline" {
  if (confidence >= 0.75) return "default";
  if (confidence >= 0.5) return "secondary";
  return "outline";
}



export function DetectionCard({ detection, index }: DetectionCardProps) {
  const confidencePercent = Math.round(detection.confidence * 100);

  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border bg-white px-4 py-3">
      <div className="flex min-w-0 items-center gap-3">
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-medium text-slate-600">
          {index + 1}
        </span>
        <div className="min-w-0">
          <p className="truncate text-sm font-medium capitalize text-slate-900">
            {detection.label}
          </p>
          <p className="text-xs text-slate-500">
            Box: ({detection.box.x1}, {detection.box.y1}) → ({detection.box.x2},{" "}
            {detection.box.y2})
          </p>
        </div>
      </div>
      <Badge variant={confidenceVariant(detection.confidence)}>
        {confidencePercent}%
      </Badge>
    </div>
  );
}
