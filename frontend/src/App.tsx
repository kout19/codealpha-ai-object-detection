import { useCallback, useState } from "react";
import { Header } from "@/components/common/Header";
import { ImageUploader } from "@/components/ImageUploader";
import { ImagePreview } from "@/components/ImagePreview";
import { LoadingState } from "@/components/LoadingState";
import { ErrorMessage } from "@/components/ErrorMessage";
import { DetectionResults } from "@/components/DetectionResult";
import { DetectionApiError, detectObjects } from "@/apiAxios/api";
import type { DetectionResponse } from "@/types/detection";

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelected = useCallback((file: File) => {
    setError(null);
    setResult(null);
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  }, []);

  const handleValidationError = useCallback((message: string) => {
    setError(message);
  }, []);

  const handleReset = useCallback(() => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setIsDetecting(false);
  }, [previewUrl]);

  const handleDetect = useCallback(async () => {
    if (!selectedFile || isDetecting) return; // prevents duplicate requests

    setIsDetecting(true);
    setError(null);

    try {
      const response = await detectObjects(selectedFile);
      setResult(response);
    } catch (err) {
      const message =
        err instanceof DetectionApiError
          ? err.message
          : "An unexpected error occurred. Please try again.";
      setError(message);
    } finally {
      setIsDetecting(false);
    }
  }, [selectedFile, isDetecting]);

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      <main className="mx-auto max-w-3xl space-y-6 px-4 py-10">
        <div className="space-y-2 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">
            Detect Objects in Any Image
          </h2>
          <p className="text-sm text-slate-500">
            Upload a photo and let YOLOv8 identify what's in it.
          </p>
        </div>

        {error && <ErrorMessage message={error} />}

        {!selectedFile && (
          <ImageUploader
            onFileSelected={handleFileSelected}
            onValidationError={handleValidationError}
            disabled={isDetecting}
          />
        )}

        {selectedFile && previewUrl && !result && (
          <ImagePreview
            previewUrl={previewUrl}
            fileName={selectedFile.name}
            fileSizeLabel={formatFileSize(selectedFile.size)}
            isDetecting={isDetecting}
            onDetect={handleDetect}
            onReset={handleReset}
          />
        )}

        {isDetecting && <LoadingState />}

        {result && !isDetecting && (
          <DetectionResults result={result} onReset={handleReset} />
        )}
      </main>
    </div>
  );
}

export default App;
