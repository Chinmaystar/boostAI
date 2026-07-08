import type { PDFMetadata, Page } from '../../mocks/extractionReview';

interface ExtractionSidebarProps {
  pdfMetadata: PDFMetadata;
  pages: Page[];
  selectedPage: number;
  onPageSelect: (pageNumber: number) => void;
}

export default function ExtractionSidebar({ pdfMetadata, pages, selectedPage, onPageSelect }: ExtractionSidebarProps) {
  return (
    <aside className="w-[280px] shrink-0 flex flex-col gap-4">
      <div className="bg-white border border-gray-200 rounded-[16px] p-5">
        <h3 className="text-[13px] font-semibold text-gray-400 uppercase tracking-wider mb-4">Document</h3>
        <div className="space-y-3">
          <div>
            <p className="text-[12px] text-gray-400 mb-0.5">File name</p>
            <p className="text-[14px] font-semibold text-gray-900 leading-snug break-words">{pdfMetadata.name}</p>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[12px] text-gray-400 mb-0.5">Pages</p>
              <p className="text-[14px] font-semibold text-gray-900">{pdfMetadata.totalPages}</p>
            </div>
            <div className="text-right">
              <p className="text-[12px] text-gray-400 mb-0.5">Questions</p>
              <p className="text-[14px] font-semibold text-gray-900">{pdfMetadata.totalQuestions}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 pt-1">
            <div className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="text-[12px] font-medium text-emerald-600">Processing complete</span>
          </div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-[16px] p-5">
        <h3 className="text-[13px] font-semibold text-gray-400 uppercase tracking-wider mb-3">Pages</h3>
        <div className="space-y-1 max-h-[400px] overflow-y-auto pr-1">
          {pages.map((page) => (
            <button
              key={page.pageNumber}
              onClick={() => onPageSelect(page.pageNumber)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-[10px] text-[14px] transition-colors ${
                selectedPage === page.pageNumber
                  ? 'bg-blue-50 text-blue-700 font-semibold'
                  : 'text-gray-600 hover:bg-gray-50 font-medium'
              }`}
            >
              <span>Page {page.pageNumber}</span>
              <span
                className={`text-[12px] px-2 py-0.5 rounded-full ${
                  selectedPage === page.pageNumber
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-500'
                }`}
              >
                {page.questionCount} {page.questionCount === 1 ? 'question' : 'questions'}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
