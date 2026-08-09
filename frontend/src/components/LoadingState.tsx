import { Loader2 } from "lucide-react";

export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border bg-white p-10 text-center">
      <Loader2 className="h-8 w-8 animate-spin text-slate-700" />
      <div>
        <p className="text-sm font-medium text-slate-900">
          Running object detection…
        </p>
        <p className="mt-1 text-xs text-slate-500">
          This may take a few seconds depending on image size.
        </p>
      </div>
    </div>
  );
}
