import { Info } from "lucide-react";

interface WebcamPanelProps {
  webcamIndex: number;
  onWebcamIndexChange: (index: number) => void;
  disabled?: boolean;
}

export function WebcamPanel({
  webcamIndex,
  onWebcamIndexChange,
  disabled,
}: WebcamPanelProps) {
  return (
    <div className="space-y-3 rounded-xl border bg-white p-4">
      <div className="flex items-start gap-2 rounded-lg bg-blue-50 p-3 text-xs text-blue-800">
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
        <p>
          This uses the camera connected to the <strong>server</strong> running
          the backend, not your browser's camera. No browser permission prompt
          will appear.
        </p>
      </div>

      <div>
        <label
          htmlFor="webcam-index"
          className="text-sm font-medium text-slate-900"
        >
          Camera device index
        </label>
        <input
          id="webcam-index"
          type="number"
          min={0}
          value={webcamIndex}
          onChange={(event) => onWebcamIndexChange(Number(event.target.value))}
          disabled={disabled}
          className="mt-1 w-24 rounded-md border border-slate-300 px-3 py-1.5 text-sm disabled:opacity-50"
        />
        <p className="mt-1 text-xs text-slate-500">
          Usually 0 for the default/built-in camera.
        </p>
      </div>
    </div>
  );
}
