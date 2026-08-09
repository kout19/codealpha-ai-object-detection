import { ScanSearch } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-10 border-b bg-white/80 backdrop-blur-sm">
      <div className="mx-auto flex max-w-3xl items-center gap-3 px-4 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-white">
          <ScanSearch className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-semibold leading-none">
            AI Object Detection
          </h1>
          <p className="mt-0.5 text-xs text-slate-500">Powered by YOLOv8</p>
        </div>
      </div>
    </header>
  );
}
