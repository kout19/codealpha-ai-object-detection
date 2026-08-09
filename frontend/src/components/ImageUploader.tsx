import {
  useCallback,
  useRef,
  useState,
  type DragEvent,
  type ChangeEvent,
} from "react";
import { ImageIcon, UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";

const ALLOWED_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // Matches backend MAX_UPLOAD_SIZE_MB=10

interface ImageUploaderProps {
  onFileSelected: (file: File) => void;
  onValidationError: (message: string) => void;
  disabled?: boolean;
}

export function ImageUploader({
  onFileSelected,
  onValidationError,
  disabled = false,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateAndSelect = useCallback(
    (file: File | undefined) => {
      if (!file) return;

      if (!ALLOWED_TYPES.includes(file.type)) {
        onValidationError(
          "Unsupported file type. Please upload a JPG, PNG, or WEBP image.",
        );
        return;
      }
      if (file.size === 0) {
        onValidationError("The selected file is empty.");
        return;
      }
      if (file.size > MAX_SIZE_BYTES) {
        onValidationError("The image is too large. Maximum size is 10MB.");
        return;
      }

      onFileSelected(file);
    },
    [onFileSelected, onValidationError],
  );

  const handleDrop = useCallback(
    (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      validateAndSelect(event.dataTransfer.files?.[0]);
    },
    [disabled, validateAndSelect],
  );

  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      validateAndSelect(event.target.files?.[0]);
      event.target.value = ""; // allows re-selecting the same file later
    },
    [validateAndSelect],
  );

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        if (!disabled) setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      aria-disabled={disabled}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors",
        isDragging
          ? "border-slate-900 bg-slate-50"
          : "border-slate-300 bg-white",
        disabled && "cursor-not-allowed opacity-50",
      )}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
        {isDragging ? (
          <UploadCloud className="h-6 w-6 text-slate-700" />
        ) : (
          <ImageIcon className="h-6 w-6 text-slate-500" />
        )}
      </div>
      <div>
        <p className="text-sm font-medium text-slate-900">
          Drag and drop an image, or click to browse
        </p>
        <p className="mt-1 text-xs text-slate-500">
          JPG, PNG, or WEBP — up to 10MB
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleInputChange}
        disabled={disabled}
      />
    </div>
  );
}
