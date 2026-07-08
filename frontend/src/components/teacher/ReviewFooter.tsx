interface ReviewFooterProps {
  canContinue: boolean;
  hasPendingQuestions: boolean;
  isSaving: boolean;
  isSaved: boolean;
  onSave: () => void;
  onContinue: () => void;
}

export default function ReviewFooter({
  canContinue,
  isSaving,
  isSaved,
  onSave,
  onContinue,
}: ReviewFooterProps) {
  return (
    <footer className="sticky bottom-0 bg-white/90 backdrop-blur-md border-t border-gray-200 px-6 py-4 z-10">
      <div className="max-w-[1400px] mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-5 py-2.5 bg-gray-900 hover:bg-black text-white font-semibold rounded-[12px] text-[14px] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10.125 2.25h-4.5c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125v-9M10.125 2.25h.375a9 9 0 0 1 9 9v.375M10.125 2.25A3.375 3.375 0 0 1 13.5 5.625v1.5c0 .621.504 1.125 1.125 1.125h1.5a3.375 3.375 0 0 1 3.375 3.375M9 15l2.25 2.25L15 12" />
                </svg>
                Save Progress
              </>
            )}
          </button>
          {isSaved && (
            <span className="text-[13px] font-medium text-emerald-600 flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
              Saved
            </span>
          )}
        </div>

        <button
          onClick={onContinue}
          disabled={!canContinue}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-[12px] text-[14px] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Continue
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </div>
    </footer>
  );
}
