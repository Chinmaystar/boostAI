import { createContext, useContext, useReducer, useCallback, useEffect, type ReactNode } from 'react';
import type { QuestionStatus, ExtractionReviewData } from '../mocks/extractionReview';
import {
  type ReviewSession,
  type ReviewSessionAction,
  type SessionStatus,
  type UploadInfo,
  type Variant,
  type QuestionVariants,
  loadSessionFromStorage,
  saveSessionToStorage,
  clearSessionFromStorage,
} from '../models/reviewSession';

function sessionReducer(state: ReviewSession | null, action: ReviewSessionAction): ReviewSession | null {
  switch (action.type) {
    case 'CREATE_SESSION': {
      const now = new Date().toISOString();
      const session: ReviewSession = {
        id: crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}`,
        status: 'ready',
        createdAt: now,
        updatedAt: now,
        pdfMetadata: action.data.pdfMetadata,
        uploadInfo: action.uploadInfo,
        pages: action.data.pages,
        questions: action.data.questions.map((q) => ({ ...q })),
        selectedPage: 1,
        isSaving: false,
        isSaved: false,
        variantData: [],
        currentVariantIndex: 0,
        compareQuestionId: null,
      };
      return session;
    }

    case 'CLEAR_SESSION': {
      return null;
    }

    case 'SET_STATUS': {
      if (!state) return state;
      return { ...state, status: action.status, updatedAt: new Date().toISOString() };
    }

    case 'APPROVE': {
      if (!state) return state;
      const questions = state.questions.map((q) =>
        q.id === action.id ? { ...q, status: 'approved' as QuestionStatus, editedText: undefined } : q
      );
      return { ...state, questions, isSaved: false, updatedAt: new Date().toISOString() };
    }

    case 'REJECT': {
      if (!state) return state;
      const questions = state.questions.map((q) =>
        q.id === action.id ? { ...q, status: 'rejected' as QuestionStatus, editedText: undefined } : q
      );
      return { ...state, questions, isSaved: false, updatedAt: new Date().toISOString() };
    }

    case 'RESET_STATUS': {
      if (!state) return state;
      const questions = state.questions.map((q) =>
        q.id === action.id ? { ...q, status: 'pending' as QuestionStatus, editedText: undefined } : q
      );
      return { ...state, questions, isSaved: false, updatedAt: new Date().toISOString() };
    }

    case 'SAVE_EDIT': {
      if (!state) return state;
      const questions = state.questions.map((q) =>
        q.id === action.id ? { ...q, status: 'edited' as QuestionStatus, editedText: action.text } : q
      );
      return { ...state, questions, isSaved: false, updatedAt: new Date().toISOString() };
    }

    case 'DUPLICATE': {
      if (!state) return state;
      const original = state.questions.find((q) => q.id === action.id);
      if (!original) return state;
      const index = state.questions.indexOf(original);
      const newId = `${original.id}-copy-${Date.now()}`;
      const duplicate = {
        ...original,
        id: newId,
        questionNumber: original.questionNumber,
        status: 'pending' as QuestionStatus,
        editedText: undefined,
      };
      const questions = [...state.questions];
      questions.splice(index + 1, 0, duplicate);
      const totalQuestions = questions.length;
      return {
        ...state,
        questions,
        pdfMetadata: { ...state.pdfMetadata, totalQuestions },
        isSaved: false,
        updatedAt: new Date().toISOString(),
      };
    }

    case 'SET_PAGE': {
      if (!state) return state;
      return { ...state, selectedPage: action.pageNumber };
    }

    case 'SAVE_PROGRESS': {
      if (!state) return state;
      return { ...state, isSaving: true };
    }

    case 'SAVE_COMPLETE': {
      if (!state) return state;
      return { ...state, isSaving: false, isSaved: true, updatedAt: new Date().toISOString() };
    }

    case 'GENERATE_VARIANTS': {
      if (!state) return state;
      return {
        ...state,
        variantData: action.variantData,
        currentVariantIndex: 0,
        compareQuestionId: null,
        status: 'reviewing',
        updatedAt: new Date().toISOString(),
      };
    }

    case 'SELECT_VARIANT': {
      if (!state) return state;
      const variantData = state.variantData.map((qv) =>
        qv.questionId === action.questionId ? { ...qv, selectedVariantId: action.variantId } : qv
      );
      return { ...state, variantData, updatedAt: new Date().toISOString() };
    }

    case 'REGENERATE_VARIANTS': {
      if (!state) return state;
      const variantData = state.variantData.map((qv) =>
        qv.questionId === action.questionId
          ? { ...qv, variants: action.variants, selectedVariantId: null }
          : qv
      );
      return { ...state, variantData, updatedAt: new Date().toISOString() };
    }

    case 'TOGGLE_FAVORITE': {
      if (!state) return state;
      const variantData: QuestionVariants[] = state.variantData.map((qv) => ({
        ...qv,
        variants: qv.variants.map((v) =>
          v.id === action.variantId ? { ...v, isFavorite: !v.isFavorite } : v
        ),
      }));
      return { ...state, variantData, updatedAt: new Date().toISOString() };
    }

    case 'SET_VARIANT_INDEX': {
      if (!state) return state;
      const maxIndex = Math.max(0, state.variantData.length - 1);
      return { ...state, currentVariantIndex: Math.min(action.index, maxIndex), updatedAt: new Date().toISOString() };
    }

    case 'SET_COMPARE': {
      if (!state) return state;
      return { ...state, compareQuestionId: action.questionId, updatedAt: new Date().toISOString() };
    }

    default:
      return state;
  }
}

interface ReviewSessionContextValue {
  session: ReviewSession | null;
  dispatch: React.Dispatch<ReviewSessionAction>;
  createSession: (data: ExtractionReviewData, uploadInfo: UploadInfo) => void;
  clearSession: () => void;
  approve: (id: string) => void;
  reject: (id: string) => void;
  resetStatus: (id: string) => void;
  saveEdit: (id: string, text: string) => void;
  duplicate: (id: string) => void;
  setPage: (pageNumber: number) => void;
  saveProgress: () => void;
  setSessionStatus: (status: SessionStatus) => void;
  generateVariants: (variantData: QuestionVariants[]) => void;
  selectVariant: (questionId: string, variantId: string) => void;
  regenerateVariants: (questionId: string, variants: Variant[]) => void;
  toggleFavorite: (variantId: string) => void;
  setVariantIndex: (index: number) => void;
  setCompare: (questionId: string | null) => void;
}

const ReviewSessionContext = createContext<ReviewSessionContextValue | null>(null);

export function ReviewSessionProvider({ children }: { children: ReactNode }) {
  const [session, dispatch] = useReducer(sessionReducer, null, () => loadSessionFromStorage());

  useEffect(() => {
    if (session) {
      saveSessionToStorage(session);
    } else {
      clearSessionFromStorage();
    }
  }, [session]);

  const createSession = useCallback(
    (data: ExtractionReviewData, uploadInfo: UploadInfo) => {
      dispatch({ type: 'CREATE_SESSION', data, uploadInfo });
    },
    []
  );

  const clearSession = useCallback(() => {
    dispatch({ type: 'CLEAR_SESSION' });
  }, []);

  const approve = useCallback((id: string) => dispatch({ type: 'APPROVE', id }), []);
  const reject = useCallback((id: string) => dispatch({ type: 'REJECT', id }), []);
  const resetStatus = useCallback((id: string) => dispatch({ type: 'RESET_STATUS', id }), []);
  const saveEdit = useCallback((id: string, text: string) => dispatch({ type: 'SAVE_EDIT', id, text }), []);
  const duplicate = useCallback((id: string) => dispatch({ type: 'DUPLICATE', id }), []);
  const setPage = useCallback((pageNumber: number) => dispatch({ type: 'SET_PAGE', pageNumber }), []);
  const setSessionStatus = useCallback((status: SessionStatus) => dispatch({ type: 'SET_STATUS', status }), []);
  const generateVariants = useCallback((variantData: QuestionVariants[]) => dispatch({ type: 'GENERATE_VARIANTS', variantData }), []);
  const selectVariant = useCallback((questionId: string, variantId: string) => dispatch({ type: 'SELECT_VARIANT', questionId, variantId }), []);
  const regenerateVariants = useCallback((questionId: string, variants: Variant[]) => dispatch({ type: 'REGENERATE_VARIANTS', questionId, variants }), []);
  const toggleFavorite = useCallback((variantId: string) => dispatch({ type: 'TOGGLE_FAVORITE', variantId }), []);
  const setVariantIndex = useCallback((index: number) => dispatch({ type: 'SET_VARIANT_INDEX', index }), []);
  const setCompare = useCallback((questionId: string | null) => dispatch({ type: 'SET_COMPARE', questionId }), []);

  const saveProgress = useCallback(() => {
    dispatch({ type: 'SAVE_PROGRESS' });
    setTimeout(() => {
      dispatch({ type: 'SAVE_COMPLETE' });
    }, 800);
  }, []);

  return (
    <ReviewSessionContext.Provider
      value={{
        session,
        dispatch,
        createSession,
        clearSession,
        approve,
        reject,
        resetStatus,
        saveEdit,
        duplicate,
        setPage,
        saveProgress,
        setSessionStatus,
        generateVariants,
        selectVariant,
        regenerateVariants,
        toggleFavorite,
        setVariantIndex,
        setCompare,
      }}
    >
      {children}
    </ReviewSessionContext.Provider>
  );
}

export function useReviewSession(): ReviewSessionContextValue {
  const ctx = useContext(ReviewSessionContext);
  if (!ctx) {
    throw new Error('useReviewSession must be used within a ReviewSessionProvider');
  }
  return ctx;
}
