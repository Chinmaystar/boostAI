import ExtractionSummary from './ExtractionSummary';

interface ExtractionToolbarProps {
  total: number;
  approved: number;
  rejected: number;
  edited: number;
  pending: number;
}

export default function ExtractionToolbar({ total, approved, rejected, edited, pending }: ExtractionToolbarProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-[16px] px-5 py-3 flex items-center justify-between">
      <ExtractionSummary
        total={total}
        approved={approved}
        rejected={rejected}
        edited={edited}
        pending={pending}
      />
      <div className="flex items-center gap-2 text-[12px] text-gray-400">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
        <span>Review each question below</span>
      </div>
    </div>
  );
}
