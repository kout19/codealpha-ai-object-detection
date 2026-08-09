import {
  useCallback,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";
import { FileVideo, UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";

const ALLOWED_TYPES = [
  "video/mp4",
  "video/webm",
  "video/quicktime",
  "video/x-msvideo",
];
const ALLOWED_EXTENSIONS = [".mp4", ".webm", ".mov", ".avi"];

interface VideoUploaderProps {
  selectedFile: File | null;
  onFileSelected: (file: File) => void;
  onValidationError: (message: string) => void;
  disabled?: boolean;
}

export function VideoUploader({
  selectedFile,
  onFileSelected,
  onValidationError,
  disabled,
}: VideoUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSelect = useCallback(
    (file: File | undefined) => {
      if (!file) return;

      const extension = file.name
        .slice(file.name.lastIndexOf("."))
        .toLowerCase();
      const typeOk =
        ALLOWED_TYPES.includes(file.type) ||
        ALLOWED_EXTENSIONS.includes(extension);

      if (!typeOk) {
        onValidationError(
          "Unsupported video format. Please upload MP4, WEBM, MOV, or AVI.",
        );
        return;
      }
      if (file.size === 0) {
        onValidationError("The selected video file is empty.");
        return;
      }

      onFileSelected(file);
    },
    [onFileSelected, onValidationError],
  );

  return (
    <div
      onDragOver={(event: DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        if (!disabled) validateAndSelect(event.dataTransfer.files?.[0]);
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      aria-disabled={disabled}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition-colors",
        isDragging
          ? "border-slate-900 bg-slate-50"
          : "border-slate-300 bg-white",
        disabled && "cursor-not-allowed opacity-50",
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
        {selectedFile ? (
          <FileVideo className="h-6 w-6 text-slate-700" />
        ) : (
          <UploadCloud className="h-6 w-6 text-slate-500" />
        )}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-900">
          {selectedFile
            ? selectedFile.name
            : "Drop a video, or click to browse"}
        </p>
        <p className="mt-1 text-xs text-slate-500">MP4, WEBM, MOV, or AVI</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="video/mp4,video/webm,video/quicktime,video/x-msvideo,.mp4,.webm,.mov,.avi"
        className="hidden"
        onChange={(event: ChangeEvent<HTMLInputElement>) => {
          validateAndSelect(event.target.files?.[0]);
          event.target.value = "";
        }}
        disabled={disabled}
      />
    </div>
  );
}
