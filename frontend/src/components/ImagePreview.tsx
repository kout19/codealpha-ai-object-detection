import { ImageOff, RotateCcw, ScanLine } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ImagePreviewProps {
  previewUrl: string;
  fileName: string;
  fileSizeLabel: string;
  isDetecting: boolean;
  onDetect: () => void;
  onReset: () => void;
}

export function ImagePreview({
  previewUrl,
  fileName,
  fileSizeLabel,
  isDetecting,
  onDetect,
  onReset,
}: ImagePreviewProps) {
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="overflow-hidden rounded-lg bg-slate-100">
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Selected preview"
            className="max-h-96 w-full object-contain"
          />
        ) : (
          <div className="flex h-64 items-center justify-center text-slate-400">
            <ImageOff className="h-8 w-8" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-slate-900">
            {fileName}
          </p>
          <p className="text-xs text-slate-500">{fileSizeLabel}</p>
        </div>

        <div className="flex shrink-0 gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onReset}
            disabled={isDetecting}
          >
            <RotateCcw className="mr-1.5 h-4 w-4" />
            Reset
          </Button>
          <Button size="sm" onClick={onDetect} disabled={isDetecting}>
            <ScanLine className="mr-1.5 h-4 w-4" />
            {isDetecting ? "Detecting..." : "Detect Objects"}
          </Button>
        </div>
      </div>
    </div>
  );
}
