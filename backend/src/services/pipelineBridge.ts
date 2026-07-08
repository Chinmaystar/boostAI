import { execFile } from "child_process";
import fs from "fs";
import path from "path";

const PIPELINE_SCRIPT = path.resolve(
  import.meta.dirname, "..", "..", "..", "content-pipeline", "main.py"
);

export interface PipelinePage {
  pageNumber: number;
  imageUrl: string;
}

export interface PipelineQuestion {
  id: string;
  questionNumber: number;
  text: string;
  type: string;
  hasDiagram: boolean;
  status: "pending";
  pageNumber: number;
}

export interface PipelineDiagram {
  id: string;
  questionNumber: string;
  page: number;
  type: string;
  bbox: { x: number; y: number; width: number; height: number };
  imageUrl: string;
}

export interface PipelineResult {
  pdfName: string;
  pageCount: number;
  questionCount: number;
  pages: PipelinePage[];
  questions: PipelineQuestion[];
  diagrams: PipelineDiagram[];
  method: string;
  tookMs: number;
  outputDir: string;
}

interface PipelineSummary {
  pdf_name: string;
  pages_processed: number;
  questions_found: number;
  diagrams_found: number;
  questions_with_diagrams: number;
  questions_without_diagrams: number;
  errors: string[];
  warnings: string[];
  output_dir: string;
}

interface RawQuestion {
  id: string;
  question_number: string;
  page_number: number;
  question_type: string;
  question_text: string;
  diagram_ids: string[];
}

interface DiagramMetadata {
  id: string;
  question_number: string;
  page: number;
  type: string;
  bbox: { x: number; y: number; width: number; height: number };
  drawing_count: number;
  text_labels: string[];
  image_count: number;
}

const TYPE_MAP: Record<string, string> = {
  computation: "short-answer",
  proof: "proof",
  construction: "construction",
  explanation: "explanation",
  diagram: "diagram",
  application: "short-answer",
};

function mapPipelineType(pipelineType: string): string {
  return TYPE_MAP[pipelineType] || "short-answer";
}

function runPipeline(pdfPath: string): Promise<PipelineSummary> {
  return new Promise((resolve, reject) => {
    const args = ["--file", pdfPath, "--json"];
    execFile("python3", [PIPELINE_SCRIPT, ...args], {
      timeout: 120_000,
      maxBuffer: 10 * 1024 * 1024,
    }, (err, stdout, stderr) => {
      if (err) {
        console.error("[pipelineBridge] stderr:", stderr);
        reject(new Error(`Pipeline failed: ${err.message}`));
        return;
      }
      try {
        const result = JSON.parse(stdout.trim()) as PipelineSummary;
        if (result.errors && result.errors.length > 0) {
          console.warn("[pipelineBridge] pipeline had errors:", result.errors);
        }
        resolve(result);
      } catch (parseErr) {
        reject(new Error(`Failed to parse pipeline output: ${parseErr}. stdout: ${stdout}`));
      }
    });
  });
}

const documentDirs = new Map<string, string>();

function readJSON<T>(filePath: string): T {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as T;
}

export function getDocumentDir(documentId: string): string | undefined {
  return documentDirs.get(documentId);
}

export async function processPDFWithPipeline(
  pdfPath: string,
  documentId: string
): Promise<PipelineResult> {
  const start = Date.now();
  const summary = await runPipeline(pdfPath);

  const outputDir = summary.output_dir;
  const rawQuestionsPath = path.join(outputDir, "raw-json", "raw_questions.json");
  const diagramMetadataPath = path.join(outputDir, "metadata", "diagram_metadata.json");

  let rawQuestions: RawQuestion[] = [];
  if (fs.existsSync(rawQuestionsPath)) {
    rawQuestions = readJSON<RawQuestion[]>(rawQuestionsPath);
  }

  let diagramMetadata: DiagramMetadata[] = [];
  if (fs.existsSync(diagramMetadataPath)) {
    diagramMetadata = readJSON<DiagramMetadata[]>(diagramMetadataPath);
  }

  const diagramByQuestion: Record<string, DiagramMetadata[]> = {};
  for (const d of diagramMetadata) {
    const qNum = d.question_number;
    if (!diagramByQuestion[qNum]) diagramByQuestion[qNum] = [];
    diagramByQuestion[qNum].push(d);
  }

  const pages: PipelinePage[] = [];
  for (let i = 1; i <= summary.pages_processed; i++) {
    pages.push({
      pageNumber: i,
      imageUrl: `/api/documents/${documentId}/pages/${i}`,
    });
  }

  let idCounter = 0;
  const questions: PipelineQuestion[] = rawQuestions.map((rq) => {
    idCounter++;
    const diagramsForQuestion = diagramByQuestion[rq.question_number] || [];
    return {
      id: `q${idCounter}`,
      questionNumber: parseInt(rq.question_number, 10) || idCounter,
      text: rq.question_text,
      type: mapPipelineType(rq.question_type),
      hasDiagram: diagramsForQuestion.length > 0,
      status: "pending" as const,
      pageNumber: rq.page_number,
    };
  });

  const diagrams: PipelineDiagram[] = diagramMetadata.map((d) => ({
    id: d.id,
    questionNumber: d.question_number,
    page: d.page,
    type: d.type,
    bbox: d.bbox,
    imageUrl: `/api/documents/${documentId}/diagrams/${d.id}`,
  }));

  const tookMs = Date.now() - start;

  documentDirs.set(documentId, outputDir);

  return {
    pdfName: summary.pdf_name,
    pageCount: summary.pages_processed,
    questionCount: summary.questions_found,
    pages,
    questions,
    diagrams,
    method: "content-pipeline",
    tookMs,
    outputDir,
  };
}
