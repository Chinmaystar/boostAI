import type { ExtractedQuestion } from '../../mocks/extractionReview';
import type { QuestionVariants } from '../../models/reviewSession';

interface VariantComparisonProps {
  question: ExtractedQuestion;
  variantData: QuestionVariants;
  onClose: () => void;
}

export default function VariantComparison({ question, variantData, onClose }: VariantComparisonProps) {
  const selectedVariant = variantData.variants.find((v) => v.id === variantData.selectedVariantId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-[24px] max-w-[960px] w-full mx-6 max-h-[85vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h3 className="text-[16px] font-bold text-gray-900">
            Compare &mdash; Question {question.questionNumber}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-[10px] text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 grid grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-6 h-6 bg-blue-50 text-blue-700 rounded-[6px] flex items-center justify-center text-[11px] font-bold">
                O
              </span>
              <span className="text-[13px] font-semibold text-gray-700">Original</span>
            </div>
            <div className="bg-blue-50/30 border border-blue-100 rounded-[12px] p-4">
              <p className="text-[14px] leading-relaxed text-gray-900 whitespace-pre-wrap">{question.text}</p>
            </div>
            {question.editedText && (
              <div className="mt-3 bg-amber-50/30 border border-amber-100 rounded-[12px] p-4">
                <p className="text-[12px] font-semibold text-amber-700 mb-1">Edited version</p>
                <p className="text-[14px] leading-relaxed text-gray-900 whitespace-pre-wrap">{question.editedText}</p>
              </div>
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              {selectedVariant ? (
                <>
                  <span className="w-6 h-6 bg-emerald-50 text-emerald-700 rounded-[6px] flex items-center justify-center text-[11px] font-bold">
                    {selectedVariant.label}
                  </span>
                  <span className="text-[13px] font-semibold text-gray-700">
                    Variant {selectedVariant.label}
                  </span>
                  <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${
                    selectedVariant.difficulty === 'easier' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    selectedVariant.difficulty === 'harder' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                    'bg-blue-50 text-blue-700 border-blue-200'
                  }`}>
                    {selectedVariant.difficulty.charAt(0).toUpperCase() + selectedVariant.difficulty.slice(1)}
                  </span>
                </>
              ) : (
                <span className="text-[13px] text-gray-400">No variant selected</span>
              )}
            </div>
            {selectedVariant ? (
              <div className="bg-emerald-50/30 border border-emerald-100 rounded-[12px] p-4">
                <p className="text-[14px] leading-relaxed text-gray-900 whitespace-pre-wrap">{selectedVariant.text}</p>
                <div className="mt-3 pt-3 border-t border-emerald-100 flex items-center gap-3 text-[12px] text-gray-500">
                  <span className="font-mono bg-white px-2 py-0.5 rounded-full">
                    {selectedVariant.templateId}
                  </span>
                  <span>
                    ~{Math.floor(selectedVariant.estimatedTime / 60)}m {selectedVariant.estimatedTime % 60}s
                  </span>
                  {selectedVariant.hasDiagram && <span>Includes diagram</span>}
                </div>
              </div>
            ) : (
              <div className="border border-dashed border-gray-200 rounded-[12px] p-8 text-center">
                <p className="text-[14px] text-gray-400">Select a variant to compare</p>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end px-6 py-4 border-t border-gray-100">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-gray-900 hover:bg-black text-white font-semibold rounded-[10px] text-[14px] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
