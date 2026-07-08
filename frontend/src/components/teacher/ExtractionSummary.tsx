interface ExtractionSummaryProps {
  total: number;
  approved: number;
  rejected: number;
  edited: number;
  pending: number;
}

export default function ExtractionSummary({ total, approved, rejected, edited, pending }: ExtractionSummaryProps) {
  const items = [
    { label: 'Total', value: total, color: 'text-gray-900', bg: 'bg-gray-100' },
    { label: 'Approved', value: approved, color: 'text-emerald-700', bg: 'bg-emerald-50' },
    { label: 'Edited', value: edited, color: 'text-blue-700', bg: 'bg-blue-50' },
    { label: 'Rejected', value: rejected, color: 'text-red-700', bg: 'bg-red-50' },
    { label: 'Pending', value: pending, color: 'text-amber-700', bg: 'bg-amber-50' },
  ];

  return (
    <div className="flex items-center gap-4">
      {items.map((item) => (
        <div
          key={item.label}
          className={`flex items-center gap-2 px-3 py-1.5 ${item.bg} rounded-lg`}
        >
          <span className={`text-[13px] font-bold ${item.color}`}>{item.value}</span>
          <span className={`text-[12px] font-medium ${item.color}`}>{item.label}</span>
        </div>
      ))}
    </div>
  );
}
