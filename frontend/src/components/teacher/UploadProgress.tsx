import type { UploadPhase } from "../../hooks/useUpload";

interface UploadProgressProps {
  phase: UploadPhase;
  progress: number;
  pagesProcessed: number;
  onCancel?: () => void;
  onRetry?: () => void;
  error?: string | null;
}

const PHASE_MESSAGES: Record<UploadPhase, { label: string; description: string } | null> = {
  idle: null,
  uploading: { label: "Uploading PDF...", description: "Sending your file to the server" },
  extracting: { label: "Extracting text...", description: "Reading each page of your document" },
  preparing: { label: "Preparing review...", description: "Almost done" },
  completed: { label: "Upload complete!", description: "Redirecting to review..." },
  error: null,
};

export default function UploadProgress({
  phase,
  progress,
  pagesProcessed,
  onCancel,
  onRetry,
  error,
}: UploadProgressProps) {
  const msg = PHASE_MESSAGES[phase];

  if (phase === "idle") return null;

  if (phase === "error") {
    return (
      <div className="w-full max-w-[560px] mx-auto">
        <div className="bg-red-50 border border-red-100 rounded-[32px] p-10 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 className="text-[22px] font-bold text-gray-900 mb-3">Upload failed</h3>
          <p className="text-[15px] text-gray-600 mb-8 max-w-[400px] mx-auto">{error || "Something went wrong. Please try again."}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-8 py-3 bg-gray-900 hover:bg-black text-white font-bold rounded-full transition-colors text-[15px]"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-[560px] mx-auto">
      <div className="bg-white border border-gray-200 rounded-[32px] p-10 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {phase === "completed" ? (
              <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
              </div>
            ) : (
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              </div>
            )}
            <div>
              <p className="text-[16px] font-bold text-gray-900">{msg?.label}</p>
              <p className="text-[13px] text-gray-500">{msg?.description}</p>
            </div>
          </div>
          {pagesProcessed > 0 && phase !== "completed" && (
            <span className="text-[13px] font-medium text-gray-400">
              Page {pagesProcessed}
            </span>
          )}
        </div>

        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out ${
              phase === "completed" ? "bg-green-500" : "bg-blue-500"
            }`}
            style={{ width: `${Math.min(100, progress)}%` }}
          />
        </div>

        <div className="flex items-center justify-between mt-3">
          <span className="text-[12px] text-gray-400 font-medium">{Math.round(progress)}%</span>
          {phase !== "completed" && onCancel && (
            <button
              onClick={onCancel}
              className="text-[12px] text-gray-400 hover:text-gray-600 font-medium underline underline-offset-2 transition-colors"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
