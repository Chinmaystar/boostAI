import { useMemo } from 'react';
import { useReviewSession } from '../context/ReviewSessionContext';

export function useExtractionReview() {
  const {
    session,
    approve,
    reject,
    resetStatus,
    saveEdit,
    duplicate,
    setPage,
    saveProgress,
  } = useReviewSession();

  const currentPageQuestions = useMemo(
    () => (session ? session.questions.filter((q) => q.pageNumber === session.selectedPage) : []),
    [session]
  );

  const counts = useMemo(() => {
    if (!session) return { total: 0, approved: 0, rejected: 0, edited: 0, pending: 0 };
    const total = session.questions.length;
    const approved = session.questions.filter((q) => q.status === 'approved').length;
    const rejected = session.questions.filter((q) => q.status === 'rejected').length;
    const edited = session.questions.filter((q) => q.status === 'edited').length;
    const pending = session.questions.filter((q) => q.status === 'pending').length;
    return { total, approved, rejected, edited, pending };
  }, [session]);

  const hasPendingQuestions = counts.pending > 0;
  const canContinue = counts.total > 0 && !hasPendingQuestions;

  return {
    session,
    state: session
      ? {
          data: {
            pdfMetadata: session.pdfMetadata,
            pages: session.pages,
            questions: session.questions,
          },
          selectedPage: session.selectedPage,
          isSaving: session.isSaving,
          isSaved: session.isSaved,
        }
      : null,
    currentPageQuestions,
    counts,
    hasPendingQuestions,
    canContinue,
    approve,
    reject,
    resetStatus,
    saveEdit,
    duplicate,
    setPage,
    saveProgress,
  };
}
