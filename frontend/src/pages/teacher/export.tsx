import { useReviewSession } from '../../context/ReviewSessionContext';
import logoImg from '../../assets/logo.avif';

export default function ExportPage() {
  const { session, clearSession } = useReviewSession();

  if (!session) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] font-sans flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  const selectedCount = session.variantData.filter((v) => v.selectedVariantId != null).length;

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans flex flex-col">
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200/60">
        <div className="max-w-[1080px] mx-auto flex items-center justify-between h-[72px] px-6">
          <a href="/" className="flex items-center gap-2.5 shrink-0">
            <img src={logoImg} alt="BoostAI" className="w-8 h-8 object-contain rounded-md" />
            <span className="text-[20px] font-extrabold tracking-tight text-gray-900">BoostAI</span>
            <span className="px-2.5 py-0.5 bg-blue-100 text-blue-600 text-[11px] font-bold rounded-full uppercase tracking-wide">Exams</span>
          </a>
          <nav className="flex items-center gap-6">
            <a href="/teacher/upload" className="text-[14px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Upload</a>
            <a href="/school" className="text-[14px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Home</a>
          </nav>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-[560px] mx-auto w-full">
          <div className="bg-white border border-gray-200 rounded-[24px] p-8 text-center">
            <div className="w-16 h-16 bg-emerald-50 rounded-[24px] flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
            </div>

            <h1 className="text-[28px] font-bold tracking-tight text-gray-900 mb-2">
              Export
            </h1>
            <p className="text-[15px] text-gray-500 mb-8">
              All questions have been reviewed and variants selected.
            </p>

            <div className="bg-gray-50 rounded-[16px] p-6 text-left space-y-4">
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <span className="text-[14px] font-medium text-gray-500">PDF name</span>
                <span className="text-[14px] font-semibold text-gray-900 text-right max-w-[280px] break-words">{session.pdfMetadata.name}</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <span className="text-[14px] font-medium text-gray-500">Total questions</span>
                <span className="text-[14px] font-semibold text-gray-900">{session.pdfMetadata.totalQuestions}</span>
              </div>
              <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                <span className="text-[14px] font-medium text-gray-500">Questions with variants</span>
                <span className="text-[14px] font-semibold text-gray-900">{selectedCount}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[14px] font-medium text-gray-500">Session status</span>
                <span className="text-[14px] font-semibold text-emerald-600">Ready for export</span>
              </div>
            </div>

            <div className="mt-8 flex items-center justify-center gap-4">
              <button
                onClick={() => { clearSession(); window.location.href = '/teacher/upload'; }}
                className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-[12px] text-[14px] transition-colors"
              >
                Start new
              </button>
              <div className="px-6 py-3 bg-gray-100 text-gray-400 font-semibold rounded-[12px] text-[14px] cursor-not-allowed">
                Export Questions
                <span className="ml-2 text-[11px]">(coming soon)</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
