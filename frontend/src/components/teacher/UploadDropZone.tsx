import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from "react";

interface UploadDropZoneProps {
  onFileAccepted: (file: File) => void;
  disabled?: boolean;
}

const MAX_FILE_SIZE = 50 * 1024 * 1024;

export default function UploadDropZone({ onFileAccepted, disabled }: UploadDropZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((f: File): string | null => {
    if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
      return "Only PDF files are accepted.";
    }
    if (f.size > MAX_FILE_SIZE) {
      return "File is too large. Maximum size is 50 MB.";
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (f: File) => {
      const err = validateFile(f);
      if (err) {
        setValidationError(err);
        setFile(null);
        return;
      }
      setValidationError(null);
      setFile(f);
      onFileAccepted(f);
    },
    [validateFile, onFileAccepted]
  );

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setDragOver(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragOver(false);
      if (disabled) return;
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) handleFile(droppedFile);
    },
    [disabled, handleFile]
  );

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0];
      if (selected) handleFile(selected);
      e.target.value = "";
    },
    [handleFile]
  );

  const handleClick = useCallback(() => {
    if (!disabled) inputRef.current?.click();
  }, [disabled]);

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") handleClick();
        }}
        aria-label="Upload PDF file"
        className={`
          relative w-full rounded-[32px] border-2 border-dashed p-12
          transition-all duration-300 cursor-pointer
          flex flex-col items-center justify-center text-center
          outline-none
          ${
            disabled
              ? "border-gray-200 bg-gray-50 cursor-not-allowed opacity-60"
              : dragOver
                ? "border-blue-400 bg-blue-50/80 scale-[1.01]"
                : "border-gray-300 bg-gray-50/50 hover:border-blue-300 hover:bg-blue-50/40 hover:shadow-sm"
          }
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleInputChange}
          disabled={disabled}
          aria-hidden="true"
        />

        {file ? (
          <>
            <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              </svg>
            </div>
            <p className="text-[18px] font-bold text-gray-900 mb-2">{file.name}</p>
            <p className="text-[14px] text-gray-500">{formatSize(file.size)}</p>
          </>
        ) : (
          <>
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-6">
              <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
              </svg>
            </div>
            {dragOver ? (
              <p className="text-[20px] font-bold text-blue-600 mb-2">Drop your PDF here</p>
            ) : (
              <>
                <p className="text-[20px] font-bold text-gray-900 mb-2">
                  Drag and drop your PDF here
                </p>
                <p className="text-[15px] text-gray-500 mb-6">or</p>
                <span className="inline-block px-8 py-3 bg-gray-900 hover:bg-black text-white font-bold rounded-full transition-colors text-[15px]">
                  Choose PDF
                </span>
              </>
            )}
          </>
        )}
      </div>

      {validationError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-100 rounded-2xl flex items-start gap-3" role="alert">
          <svg className="w-5 h-5 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
          </svg>
          <p className="text-[14px] text-red-700 font-medium">{validationError}</p>
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[13px] text-gray-400">
        <span className="flex items-center gap-1.5">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          PDF files only
        </span>
        <span className="flex items-center gap-1.5">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          Max 50 MB
        </span>
        <span className="flex items-center gap-1.5">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          Secure & encrypted
        </span>
      </div>
    </div>
  );
}
