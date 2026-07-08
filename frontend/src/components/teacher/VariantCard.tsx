import type { Variant } from '../../models/reviewSession';

interface VariantCardProps {
  variant: Variant;
  isSelected: boolean;
  onSelect: () => void;
  onFavorite: () => void;
  onCompare: () => void;
}

const DIFFICULTY_CONFIG = {
  easier: { label: 'Easier', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  similar: { label: 'Similar', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  harder: { label: 'Harder', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};

export default function VariantCard({ variant, isSelected, onSelect, onFavorite, onCompare }: VariantCardProps) {
  const dc = DIFFICULTY_CONFIG[variant.difficulty];

  return (
    <div
      className={`bg-white border rounded-[16px] overflow-hidden transition-all ${
        isSelected ? 'border-emerald-400 ring-2 ring-emerald-100' : 'border-gray-200 hover:shadow-sm'
      }`}
    >
      <div className="px-4 py-3 flex items-center justify-between border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span
            className={`w-7 h-7 rounded-[8px] flex items-center justify-center text-[13px] font-bold ${
              isSelected ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500'
            }`}
          >
            {variant.label}
          </span>
          <span className={`text-[12px] font-semibold px-2 py-0.5 rounded-full ${dc.bg} ${dc.text} ${dc.border} border`}>
            {dc.label}
          </span>
          <span className="text-[12px] text-gray-400 font-mono bg-gray-50 px-2 py-0.5 rounded-full">
            {variant.templateId}
          </span>
          {variant.hasDiagram && (
            <span className="flex items-center gap-1 text-[12px] text-gray-400 font-medium">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
              </svg>
              Diagram
            </span>
          )}
        </div>
        <span className="text-[12px] text-gray-400 font-medium flex items-center gap-1">
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
          </svg>
          {Math.floor(variant.estimatedTime / 60)}m {variant.estimatedTime % 60}s
        </span>
      </div>

      <div className="px-4 py-4">
        <p className="text-[15px] leading-relaxed text-gray-900 whitespace-pre-wrap">{variant.text}</p>
      </div>

      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <button
            onClick={onSelect}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-[10px] text-[13px] font-semibold transition-colors ${
              isSelected
                ? 'bg-emerald-100 text-emerald-700'
                : 'bg-white border border-gray-200 text-gray-600 hover:border-emerald-300 hover:text-emerald-600'
            }`}
          >
            {isSelected ? (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                Selected
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
                Select
              </>
            )}
          </button>
          <button
            onClick={onCompare}
            className="flex items-center gap-1.5 px-3 py-2 bg-white border border-gray-200 text-gray-600 hover:text-blue-600 hover:border-blue-300 rounded-[10px] text-[13px] font-semibold transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
            </svg>
            Compare
          </button>
        </div>
        <button
          onClick={onFavorite}
          className={`p-2 rounded-[8px] transition-colors ${
            variant.isFavorite
              ? 'text-amber-500 hover:text-amber-600'
              : 'text-gray-300 hover:text-amber-400'
          }`}
          title={variant.isFavorite ? 'Remove from favorites' : 'Mark as favorite'}
        >
          <svg className="w-5 h-5" fill={variant.isFavorite ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />
          </svg>
        </button>
      </div>
    </div>
  );
}
