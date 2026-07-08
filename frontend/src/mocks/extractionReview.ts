export type QuestionStatus = 'pending' | 'approved' | 'rejected' | 'edited';

export interface ExtractedQuestion {
  id: string;
  questionNumber: number;
  text: string;
  type?: string;
  hasDiagram: boolean;
  status: QuestionStatus;
  pageNumber: number;
  editedText?: string;
}

export interface PDFMetadata {
  name: string;
  totalPages: number;
  totalQuestions: number;
  processingStatus: 'completed';
  uploadedAt: string;
}

export interface Page {
  pageNumber: number;
  questionCount: number;
}

export interface ExtractionReviewData {
  pdfMetadata: PDFMetadata;
  pages: Page[];
  questions: ExtractedQuestion[];
}

export const MOCK_EXTRACTION_REVIEW: ExtractionReviewData = {
  pdfMetadata: {
    name: 'AQA-GCSE-Mathematics-Higher-Paper-1.pdf',
    totalPages: 8,
    totalQuestions: 16,
    processingStatus: 'completed',
    uploadedAt: '2026-07-08T10:30:00Z',
  },
  pages: [
    { pageNumber: 1, questionCount: 2 },
    { pageNumber: 2, questionCount: 2 },
    { pageNumber: 3, questionCount: 2 },
    { pageNumber: 4, questionCount: 2 },
    { pageNumber: 5, questionCount: 2 },
    { pageNumber: 6, questionCount: 2 },
    { pageNumber: 7, questionCount: 2 },
    { pageNumber: 8, questionCount: 2 },
  ],
  questions: [
    {
      id: 'q1',
      questionNumber: 1,
      text: 'Solve 3x + 7 = 22',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 1,
    },
    {
      id: 'q2',
      questionNumber: 2,
      text: 'Factorise x² + 5x + 6',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 1,
    },
    {
      id: 'q3',
      questionNumber: 3,
      text: 'Calculate the area of a circle with radius 4 cm. Give your answer in terms of π.',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 2,
    },
    {
      id: 'q4',
      questionNumber: 4,
      text: 'A bag contains 5 red balls, 3 blue balls and 2 green balls. A ball is chosen at random. What is the probability that it is not blue?',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 2,
    },
    {
      id: 'q5',
      questionNumber: 5,
      text: 'Solve the simultaneous equations:\n2x + y = 7\nx - y = 2',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 3,
    },
    {
      id: 'q6',
      questionNumber: 6,
      text: 'Expand and simplify (x + 3)(x - 4)',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 3,
    },
    {
      id: 'q7',
      questionNumber: 7,
      text: 'The diagram shows a right-angled triangle. Calculate the length of the hypotenuse.',
      type: 'short-answer',
      hasDiagram: true,
      status: 'pending',
      pageNumber: 4,
    },
    {
      id: 'q8',
      questionNumber: 8,
      text: 'Differentiate y = 3x² + 2x - 5 with respect to x.',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 4,
    },
    {
      id: 'q9',
      questionNumber: 9,
      text: 'A car travels 120 miles in 2 hours 30 minutes. Calculate its average speed in miles per hour.',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 5,
    },
    {
      id: 'q10',
      questionNumber: 10,
      text: 'Solve the inequality 4x - 7 ≤ 2x + 5',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 5,
    },
    {
      id: 'q11',
      questionNumber: 11,
      text: 'The graph of y = f(x) is shown on the grid. Sketch the graph of y = 2f(x).',
      type: 'short-answer',
      hasDiagram: true,
      status: 'pending',
      pageNumber: 6,
    },
    {
      id: 'q12',
      questionNumber: 12,
      text: 'Prove that the sum of any three consecutive integers is a multiple of 3.',
      type: 'proof',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 6,
    },
    {
      id: 'q13',
      questionNumber: 13,
      text: 'A sequence has nth term = 3n² - 2. Find the first three terms of the sequence.',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 7,
    },
    {
      id: 'q14',
      questionNumber: 14,
      text: 'Calculate the volume of a cylinder with radius 3 cm and height 8 cm. Give your answer to 3 significant figures.',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 7,
    },
    {
      id: 'q15',
      questionNumber: 15,
      text: 'The Venn diagram shows the number of students who study French (F) and Spanish (S). Find P(F ∪ S).',
      type: 'short-answer',
      hasDiagram: true,
      status: 'pending',
      pageNumber: 8,
    },
    {
      id: 'q16',
      questionNumber: 16,
      text: 'f(x) = 2x² - 5x + 3. Find the coordinates of the turning point of f(x).',
      type: 'short-answer',
      hasDiagram: false,
      status: 'pending',
      pageNumber: 8,
    },
  ],
};
