import { Download, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DetectionCard } from "@/components/DetectionCard";
import { getFullImageUrl } from "@/apiAxios/api";
import type { DetectionResponse } from "@/types/detection";

interface DetectionResultsProps {
  result: DetectionResponse;
  onReset: () => void;
}

export function DetectionResults({ result, onReset }: DetectionResultsProps) {
  const fullImageUrl = getFullImageUrl(result.image_url);

  const handleDownload = async () => {
    const response = await fetch(fullImageUrl);
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = "detection-result.jpg";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(blobUrl);
  };

  return (
    <div className="space-y-4">
      <div className="rounded-xl border bg-white p-4">
        <img
          src={fullImageUrl}
          alt="Annotated detection result"
          className="max-h-[32rem] w-full rounded-lg bg-slate-100 object-contain"
        />

        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-600">
            <span className="font-semibold text-slate-900">{result.count}</span>{" "}
            {result.count === 1 ? "object" : "objects"} detected
          </p>

          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onReset}>
              <RotateCcw className="mr-1.5 h-4 w-4" />
              Detect Another Image
            </Button>
            <Button size="sm" onClick={handleDownload}>
              <Download className="mr-1.5 h-4 w-4" />
              Download Result
            </Button>
          </div>
        </div>
      </div>

      {result.detections.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-900">
            Detected Objects
          </h3>
          <div className="space-y-2">
            {result.detections.map((detection, index) => (
              <DetectionCard
                key={`${detection.label}-${index}`}
                detection={detection}
                index={index}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
