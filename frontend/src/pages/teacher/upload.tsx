import { useCallback, useEffect, useRef } from "react";
import { useUpload } from "../../hooks/useUpload";
import { useReviewSession } from "../../context/ReviewSessionContext";
import UploadDropZone from "../../components/teacher/UploadDropZone";
import UploadProgress from "../../components/teacher/UploadProgress";
import logoImg from "../../assets/logo.avif";

const RECENT_PAPERS: { name: string; date: string; pages: number }[] = [];

export default function TeacherUploadPage() {
  const { phase, progress, pagesProcessed, error, result, extractionData, start, cancel } = useUpload();
  const { createSession } = useReviewSession();
  const redirectingRef = useRef(false);

  useEffect(() => {
    if (phase === "completed" && extractionData && !redirectingRef.current) {
      redirectingRef.current = true;

      createSession(extractionData, {
        fileName: extractionData.pdfMetadata.name,
        fileSize: 0,
        uploadedAt: new Date().toISOString(),
        documentId: result?.documentId,
      });

      const timer = setTimeout(() => {
        window.location.href = "/teacher/extraction-review";
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [phase, extractionData, result, createSession]);

  const handleFileAccepted = useCallback(
    (file: File) => {
      redirectingRef.current = false;
      start(file);
    },
    [start]
  );

  const handleRetry = useCallback(() => {
    cancel();
  }, [cancel]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans">
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/60">
        <div className="max-w-[1080px] mx-auto flex items-center justify-between h-[72px] px-6">
          <a href="/" className="flex items-center gap-2.5 shrink-0">
            <img src={logoImg} alt="BoostAI" className="w-8 h-8 object-contain rounded-md" />
            <span className="text-[20px] font-extrabold tracking-tight text-gray-900">
              BoostAI
            </span>
            <span className="px-2.5 py-0.5 bg-blue-100 text-blue-600 text-[11px] font-bold rounded-full uppercase tracking-wide">
              Exams
            </span>
          </a>
          <nav className="flex items-center gap-6">
            <a
              href="/teacher/upload"
              className="text-[14px] font-semibold text-blue-600 border-b-2 border-blue-600 pb-0.5"
            >
              Upload
            </a>
            <a href="/school" className="text-[14px] font-medium text-gray-500 hover:text-gray-800 transition-colors">
              Home
            </a>
          </nav>
        </div>
      </header>

      <main className="max-w-[1080px] mx-auto px-6 pt-16 pb-32">
        <div className="max-w-[640px] mx-auto">
          <h1 className="text-[36px] md:text-[44px] font-bold tracking-tight text-gray-900 mb-4">
            Upload Exam Paper
          </h1>
          <p className="text-[16px] text-gray-500 mb-10 leading-relaxed">
            Upload a PDF of an exam paper. BoostAI will extract the questions and prepare them for review.
          </p>
        </div>

        <div className="max-w-[640px] mx-auto">
          {phase === "idle" || phase === "error" ? (
            <UploadDropZone onFileAccepted={handleFileAccepted} disabled={false} />
          ) : (
            <UploadProgress
              phase={phase}
              progress={progress}
              pagesProcessed={pagesProcessed}
              onCancel={cancel}
              onRetry={handleRetry}
              error={error}
            />
          )}
        </div>

        <div className="max-w-[640px] mx-auto mt-20">
          <div className="border-t border-gray-200 pt-12">
            <h2 className="text-[18px] font-bold text-gray-900 mb-6">Recently uploaded</h2>
            {RECENT_PAPERS.length === 0 ? (
              <div className="bg-white border border-gray-100 rounded-[24px] p-10 text-center">
                <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                  </svg>
                </div>
                <p className="text-[15px] text-gray-500 font-medium">No papers uploaded yet</p>
                <p className="text-[13px] text-gray-400 mt-1">Uploaded papers will appear here.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {RECENT_PAPERS.map((paper, i) => (
                  <div
                    key={i}
                    className="bg-white border border-gray-100 rounded-[16px] p-5 flex items-center justify-between hover:border-gray-200 hover:shadow-sm transition-all cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                        <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                        </svg>
                      </div>
                      <div>
                        <p className="text-[15px] font-bold text-gray-900">{paper.name}</p>
                        <p className="text-[12px] text-gray-400">{paper.date} &middot; {paper.pages} pages</p>
                      </div>
                    </div>
                    <svg className="w-5 h-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                    </svg>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
