import type { PDFMetadata, Page, ExtractedQuestion, ExtractionReviewData } from '../mocks/extractionReview';

export type SessionStatus = 'creating' | 'ready' | 'reviewing' | 'completed';

export interface UploadInfo {
  fileName: string;
  fileSize?: number;
  uploadedAt: string;
  documentId?: string;
}

export interface Variant {
  id: string;
  label: string;
  text: string;
  difficulty: 'easier' | 'similar' | 'harder';
  templateId: string;
  estimatedTime: number;
  hasDiagram: boolean;
  isFavorite: boolean;
}

export interface QuestionVariants {
  questionId: string;
  variants: Variant[];
  selectedVariantId: string | null;
}

export interface ReviewSession {
  id: string;
  status: SessionStatus;
  createdAt: string;
  updatedAt: string;
  pdfMetadata: PDFMetadata;
  uploadInfo: UploadInfo;
  pages: Page[];
  questions: ExtractedQuestion[];
  selectedPage: number;
  isSaving: boolean;
  isSaved: boolean;
  variantData: QuestionVariants[];
  currentVariantIndex: number;
  compareQuestionId: string | null;
}

export type ReviewSessionAction =
  | { type: 'CREATE_SESSION'; data: ExtractionReviewData; uploadInfo: UploadInfo }
  | { type: 'CLEAR_SESSION' }
  | { type: 'APPROVE'; id: string }
  | { type: 'REJECT'; id: string }
  | { type: 'RESET_STATUS'; id: string }
  | { type: 'SAVE_EDIT'; id: string; text: string }
  | { type: 'DUPLICATE'; id: string }
  | { type: 'SET_PAGE'; pageNumber: number }
  | { type: 'SAVE_PROGRESS' }
  | { type: 'SAVE_COMPLETE' }
  | { type: 'SET_STATUS'; status: SessionStatus }
  | { type: 'GENERATE_VARIANTS'; variantData: QuestionVariants[] }
  | { type: 'SELECT_VARIANT'; questionId: string; variantId: string }
  | { type: 'REGENERATE_VARIANTS'; questionId: string; variants: Variant[] }
  | { type: 'TOGGLE_FAVORITE'; variantId: string }
  | { type: 'SET_VARIANT_INDEX'; index: number }
  | { type: 'SET_COMPARE'; questionId: string | null };

const SESSION_STORAGE_KEY = 'boostai_review_session';

export function loadSessionFromStorage(): ReviewSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as ReviewSession;
  } catch {
    return null;
  }
}

export function saveSessionToStorage(session: ReviewSession): void {
  try {
    sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
  } catch {
    /* storage full or unavailable */
  }
}

export function clearSessionFromStorage(): void {
  try {
    sessionStorage.removeItem(SESSION_STORAGE_KEY);
  } catch {
    /* ignore */
  }
}
