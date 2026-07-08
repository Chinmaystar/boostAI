import type { ExtractedQuestion } from '../../mocks/extractionReview';
import type { QuestionVariants } from '../../models/reviewSession';

interface GenerationSidebarProps {
  questions: ExtractedQuestion[];
  variantData: QuestionVariants[];
  currentIndex: number;
  pdfName: string;
  totalApproved: number;
  onSelectQuestion: (index: number) => void;
}

export default function GenerationSidebar({
  questions,
  variantData,
  currentIndex,
  pdfName,
  totalApproved,
  onSelectQuestion,
}: GenerationSidebarProps) {
  return (
    <aside className="w-[280px] shrink-0 flex flex-col gap-4">
      <div className="bg-white border border-gray-200 rounded-[16px] p-5">
        <h3 className="text-[13px] font-semibold text-gray-400 uppercase tracking-wider mb-4">Document</h3>
        <div className="space-y-3">
          <div>
            <p className="text-[12px] text-gray-400 mb-0.5">PDF name</p>
            <p className="text-[14px] font-semibold text-gray-900 leading-snug break-words">{pdfName}</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[12px] text-gray-400 mb-0.5">Approved</p>
              <p className="text-[14px] font-semibold text-gray-900">{totalApproved}</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-right">
                <p className="text-[12px] text-gray-400 mb-0.5">Reviewed</p>
                <p className="text-[14px] font-semibold text-gray-900">
                  {variantData.filter((v) => v.selectedVariantId).length} / {totalApproved}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-[16px] p-5">
        <h3 className="text-[13px] font-semibold text-gray-400 uppercase tracking-wider mb-3">Questions</h3>
        <div className="space-y-1 max-h-[420px] overflow-y-auto pr-1">
          {questions.map((q, index) => {
            const qv = variantData.find((v) => v.questionId === q.id);
            const isSelected = qv?.selectedVariantId != null;
            return (
              <button
                key={q.id}
                onClick={() => onSelectQuestion(index)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-[14px] transition-colors text-left ${
                  index === currentIndex
                    ? 'bg-blue-50 text-blue-700 font-semibold'
                    : 'text-gray-600 hover:bg-gray-50 font-medium'
                }`}
              >
                <span
                  className={`w-6 h-6 rounded-[8px] flex items-center justify-center text-[12px] font-bold shrink-0 ${
                    isSelected
                      ? 'bg-emerald-100 text-emerald-700'
                      : index === currentIndex
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {isSelected ? (
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                  ) : (
                    q.questionNumber
                  )}
                </span>
                <span className="truncate">{q.text.split('\n')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
