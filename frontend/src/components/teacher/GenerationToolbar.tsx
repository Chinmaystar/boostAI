interface GenerationToolbarProps {
  currentIndex: number;
  totalQuestions: number;
  hasSelectedVariant: boolean;
  onPrevious: () => void;
  onNext: () => void;
  onContinue: () => void;
}

export default function GenerationToolbar({
  currentIndex,
  totalQuestions,
  hasSelectedVariant,
  onPrevious,
  onNext,
  onContinue,
}: GenerationToolbarProps) {
  return (
    <footer className="sticky bottom-0 bg-white/90 backdrop-blur-md border-t border-gray-200 px-6 py-4 z-10">
      <div className="max-w-[1400px] mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={onPrevious}
            disabled={currentIndex === 0}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 font-semibold rounded-[10px] text-[14px] transition-colors hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
            Previous
          </button>

          <div className="text-[14px] font-medium text-gray-500">
            <span className="text-gray-900 font-semibold">{currentIndex + 1}</span> of {totalQuestions}
          </div>

          <button
            onClick={onNext}
            disabled={currentIndex === totalQuestions - 1}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 text-gray-700 font-semibold rounded-[10px] text-[14px] transition-colors hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            Next
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
            </svg>
          </button>
        </div>

        <button
          onClick={onContinue}
          disabled={!hasSelectedVariant}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-[10px] text-[14px] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
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
