import { useCallback, useEffect } from 'react';
import { useExtractionReview } from '../../hooks/useExtractionReview';
import ExtractionSidebar from '../../components/teacher/ExtractionSidebar';
import ExtractionToolbar from '../../components/teacher/ExtractionToolbar';
import PagePreview from '../../components/teacher/PagePreview';
import QuestionCard from '../../components/teacher/QuestionCard';
import ReviewFooter from '../../components/teacher/ReviewFooter';
import logoImg from '../../assets/logo.avif';

export default function ExtractionReviewPage() {
  const {
    session,
    state,
    currentPageQuestions,
    counts,
    canContinue,
    approve,
    reject,
    resetStatus,
    saveEdit,
    duplicate,
    setPage,
    saveProgress,
  } = useExtractionReview();

  useEffect(() => {
    if (!session) {
      window.location.href = '/teacher/upload';
    }
  }, [session]);

  const handleContinue = useCallback(() => {
    window.location.href = '/teacher/question-generation';
  }, []);

  if (!session || !state) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] font-sans flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans flex flex-col">
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/60">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between h-[64px] px-6">
          <a href="/" className="flex items-center gap-2.5 shrink-0">
            <img src={logoImg} alt="BoostAI" className="w-7 h-7 object-contain rounded-md" />
            <span className="text-[18px] font-extrabold tracking-tight text-gray-900">BoostAI</span>
            <span className="px-2 py-0.5 bg-blue-100 text-blue-600 text-[11px] font-bold rounded-full uppercase tracking-wide">Exams</span>
          </a>
          <nav className="flex items-center gap-5">
            <a
              href="/teacher/upload"
              className="text-[13px] font-medium text-gray-500 hover:text-gray-800 transition-colors"
            >
              Upload
            </a>
            <a
              href="/teacher/extraction-review"
              className="text-[13px] font-semibold text-blue-600 border-b-2 border-blue-600 pb-0.5"
            >
              Review
            </a>
            <a href="/school" className="text-[13px] font-medium text-gray-500 hover:text-gray-800 transition-colors">
              Home
            </a>
          </nav>
        </div>
      </header>

      <div className="flex-1 flex px-6 py-6 gap-6 max-w-[1400px] mx-auto w-full">
        <ExtractionSidebar
          pdfMetadata={state.data.pdfMetadata}
          pages={state.data.pages}
          selectedPage={session.selectedPage}
          onPageSelect={setPage}
        />

        <main className="flex-1 min-w-0 flex flex-col gap-4 pb-24">
          <ExtractionToolbar
            total={counts.total}
            approved={counts.approved}
            rejected={counts.rejected}
            edited={counts.edited}
            pending={counts.pending}
          />

          <PagePreview pageNumber={session.selectedPage} documentId={session.uploadInfo.documentId} />

          {currentPageQuestions.length > 0 ? (
            <div className="space-y-3">
              {currentPageQuestions.map((question) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  onApprove={approve}
                  onReject={reject}
                  onSaveEdit={saveEdit}
                  onResetStatus={resetStatus}
                  onDuplicate={duplicate}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-[16px] p-8 text-center">
              <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z" />
                </svg>
              </div>
              <p className="text-[15px] text-gray-500 font-medium">No questions on this page</p>
              <p className="text-[13px] text-gray-400 mt-1">Select a different page to review questions.</p>
            </div>
          )}
        </main>
      </div>

      <ReviewFooter
        canContinue={canContinue}
        hasPendingQuestions={counts.pending > 0}
        isSaving={session.isSaving}
        isSaved={session.isSaved}
        onSave={saveProgress}
        onContinue={handleContinue}
      />
    </div>
  );
}
