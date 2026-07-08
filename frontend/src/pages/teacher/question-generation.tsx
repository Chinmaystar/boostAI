import { useEffect, useCallback, useMemo } from 'react';
import { useReviewSession } from '../../context/ReviewSessionContext';
import { MOCK_VARIANTS } from '../../mocks/questionVariants';
import GenerationSidebar from '../../components/teacher/GenerationSidebar';
import VariantCard from '../../components/teacher/VariantCard';
import VariantComparison from '../../components/teacher/VariantComparison';
import GenerationToolbar from '../../components/teacher/GenerationToolbar';
import logoImg from '../../assets/logo.avif';

export default function QuestionGenerationPage() {
  const {
    session,
    generateVariants,
    selectVariant,
    regenerateVariants,
    toggleFavorite,
    setVariantIndex,
    setCompare,
  } = useReviewSession();

  const reviewQuestions = useMemo(() => {
    if (!session) return [];
    return session.questions.filter((q) => q.status === 'approved' || q.status === 'edited');
  }, [session]);

  useEffect(() => {
    if (session && session.variantData.length === 0 && reviewQuestions.length > 0) {
      const variantData = reviewQuestions.map((q) => ({
        questionId: q.id,
        variants: MOCK_VARIANTS[q.id] || [],
        selectedVariantId: null,
      }));
      generateVariants(variantData);
    }
  }, [session, reviewQuestions, generateVariants]);

  const currentQuestion = reviewQuestions[session?.currentVariantIndex ?? 0] ?? null;
  const currentVariantData = useMemo(() => {
    if (!currentQuestion || !session) return null;
    return session.variantData.find((v) => v.questionId === currentQuestion.id) ?? null;
  }, [currentQuestion, session]);

  const allHaveSelection = useMemo(() => {
    if (!session) return false;
    if (session.variantData.length === 0) return false;
    return session.variantData.every((v) => v.selectedVariantId != null);
  }, [session]);

  const handleContinue = useCallback(() => {
    window.location.href = '/teacher/export';
  }, []);

  const handleRegenerate = useCallback(() => {
    if (!currentQuestion) return;
    const newVariants = MOCK_VARIANTS[currentQuestion.id];
    if (!newVariants) return;
    const shuffled = [...newVariants].sort(() => Math.random() - 0.5);
    const relabeled = shuffled.map((v, i) => ({
      ...v,
      id: `${v.id}-reg-${Date.now()}`,
      label: String.fromCharCode(65 + i),
      isFavorite: false,
    }));
    regenerateVariants(currentQuestion.id, relabeled);
  }, [currentQuestion, regenerateVariants]);

  const handleSelectVariant = useCallback(
    (variantId: string) => {
      if (!currentQuestion) return;
      selectVariant(currentQuestion.id, variantId);
    },
    [currentQuestion, selectVariant]
  );

  const handleFavorite = useCallback(
    (variantId: string) => {
      toggleFavorite(variantId);
    },
    [toggleFavorite]
  );

  const handleCompare = useCallback(() => {
    if (!currentQuestion) return;
    setCompare(currentQuestion.id);
  }, [currentQuestion, setCompare]);

  const handleCloseCompare = useCallback(() => {
    setCompare(null);
  }, [setCompare]);

  if (!session) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] font-sans flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (reviewQuestions.length === 0) {
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
              <a href="/teacher/extraction-review" className="text-[14px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Review</a>
              <a href="/school" className="text-[14px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Home</a>
            </nav>
          </div>
        </header>
        <main className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-[480px] mx-auto text-center">
            <div className="w-16 h-16 bg-amber-50 rounded-[24px] flex items-center justify-center mx-auto mb-6">
              <svg className="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
              </svg>
            </div>
            <h1 className="text-[28px] font-bold tracking-tight text-gray-900 mb-3">No approved questions</h1>
            <p className="text-[15px] text-gray-500 mb-8 leading-relaxed">Please approve or edit questions in the extraction review first.</p>
            <a href="/teacher/extraction-review" className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 hover:bg-black text-white font-bold rounded-full transition-colors text-[15px]">
              Go to Review
            </a>
          </div>
        </main>
      </div>
    );
  }

  const compareQuestion = session.compareQuestionId
    ? session.questions.find((q) => q.id === session.compareQuestionId)
    : null;

  const compareVariantData = session.compareQuestionId
    ? session.variantData.find((v) => v.questionId === session.compareQuestionId)
    : null;

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
            <a href="/teacher/upload" className="text-[13px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Upload</a>
            <a href="/teacher/extraction-review" className="text-[13px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Review</a>
            <a href="/teacher/question-generation" className="text-[13px] font-semibold text-blue-600 border-b-2 border-blue-600 pb-0.5">Generate</a>
            <a href="/school" className="text-[13px] font-medium text-gray-500 hover:text-gray-800 transition-colors">Home</a>
          </nav>
        </div>
      </header>

      <div className="flex-1 flex px-6 py-6 gap-6 max-w-[1400px] mx-auto w-full">
        <GenerationSidebar
          questions={reviewQuestions}
          variantData={session.variantData}
          currentIndex={session.currentVariantIndex}
          pdfName={session.pdfMetadata.name}
          totalApproved={reviewQuestions.length}
          onSelectQuestion={(index) => setVariantIndex(index)}
        />

        <main className="flex-1 min-w-0 flex flex-col gap-4 pb-24">
          {currentQuestion && (
            <div className="bg-white border border-gray-200 rounded-[16px] p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-6 h-6 bg-gray-100 text-gray-500 rounded-[6px] flex items-center justify-center text-[12px] font-bold">
                  {currentQuestion.questionNumber}
                </span>
                <span className="text-[13px] font-semibold text-gray-400 uppercase tracking-wider">Original</span>
                {currentQuestion.hasDiagram && (
                  <span className="flex items-center gap-1 text-[12px] text-gray-400 font-medium">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                    </svg>
                    Diagram
                  </span>
                )}
              </div>
              <p className="text-[15px] leading-relaxed text-gray-900 whitespace-pre-wrap">
                {currentQuestion.editedText ?? currentQuestion.text}
              </p>
              {currentQuestion.editedText && (
                <p className="text-[12px] text-amber-600 mt-2 font-medium">
                  Edited version shown. Original: &ldquo;{currentQuestion.text}&rdquo;
                </p>
              )}
            </div>
          )}

          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h5.25m5.25-.75L17.25 9m0 0L21 12.75M17.25 9v12" />
            </svg>
            <span className="text-[13px] font-medium text-gray-500">
              Generated Variants
              {currentVariantData?.selectedVariantId
                ? ` \u2014 Variant ${currentVariantData.variants.find((v) => v.id === currentVariantData.selectedVariantId)?.label} selected`
                : ' \u2014 Select a variant'}
            </span>
          </div>

          {currentVariantData && currentVariantData.variants.length > 0 ? (
            <div className="grid grid-cols-3 gap-4">
              {currentVariantData.variants.map((variant) => (
                <VariantCard
                  key={variant.id}
                  variant={variant}
                  isSelected={currentVariantData.selectedVariantId === variant.id}
                  onSelect={() => handleSelectVariant(variant.id)}
                  onFavorite={() => handleFavorite(variant.id)}
                  onCompare={handleCompare}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white border border-gray-200 rounded-[16px] p-8 text-center">
              <p className="text-[15px] text-gray-500 font-medium">No variants generated</p>
              <button
                onClick={handleRegenerate}
                className="mt-4 px-5 py-2.5 bg-gray-900 hover:bg-black text-white font-semibold rounded-[10px] text-[14px] transition-colors"
              >
                Generate Variants
              </button>
            </div>
          )}

          {currentVariantData && currentVariantData.selectedVariantId && (
            <div className="flex justify-end">
              <button
                onClick={handleRegenerate}
                className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-600 hover:text-gray-800 rounded-[10px] text-[13px] font-semibold transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182" />
                </svg>
                Regenerate All
              </button>
            </div>
          )}
        </main>
      </div>

      <GenerationToolbar
        currentIndex={session.currentVariantIndex}
        totalQuestions={reviewQuestions.length}
        hasSelectedVariant={allHaveSelection}
        onPrevious={() => setVariantIndex(session.currentVariantIndex - 1)}
        onNext={() => setVariantIndex(session.currentVariantIndex + 1)}
        onContinue={handleContinue}
      />

      {compareQuestion && compareVariantData && (
        <VariantComparison
          question={compareQuestion}
          variantData={compareVariantData}
          onClose={handleCloseCompare}
        />
      )}
    </div>
  );
}
