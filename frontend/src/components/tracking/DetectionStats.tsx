import type { TrackingSourceType, TrackingUIStatus } from "@/types/tracking";

interface DetectionStatsProps {
  activeObjects: number;
  fps: number | null;
  mode: TrackingSourceType;
  status: TrackingUIStatus;
}

export function DetectionStats({
  activeObjects,
  fps,
  mode,
  status,
}: DetectionStatsProps) {
  const rows: { label: string; value: string }[] = [
    { label: "Active Tracks", value: activeObjects.toString() },
    { label: "Source", value: mode === "webcam" ? "Webcam" : "Video File" },
    { label: "Status", value: status === "tracking" ? "Tracking" : "Idle" },
  ];

  if (fps !== null) {
    rows.push({ label: "FPS", value: fps.toFixed(1) });
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {rows.map((row) => (
        <div key={row.label} className="rounded-lg border bg-white p-3">
          <p className="text-xs text-slate-500">{row.label}</p>
          <p className="mt-1 text-lg font-semibold text-slate-900">
            {row.value}
          </p>
        </div>
      ))}
    </div>
  );
}
