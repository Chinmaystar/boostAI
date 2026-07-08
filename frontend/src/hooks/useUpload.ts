import { useState, useRef, useCallback } from "react";
import type { ExtractionReviewData } from "../mocks/extractionReview";

export type UploadPhase =
  | "idle"
  | "uploading"
  | "extracting"
  | "preparing"
  | "completed"
  | "error";

export interface UploadResult {
  method: string;
  pageCount: number;
  tookMs: number;
  documentId: string;
}

const BACKEND_URL = "http://localhost:3001";

export function useUpload() {
  const [phase, setPhase] = useState<UploadPhase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [pagesProcessed, setPagesProcessed] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [extractionData, setExtractionData] = useState<ExtractionReviewData | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setPhase("idle");
    setProgress(0);
    setPagesProcessed(0);
    setTotalPages(0);
    setError(null);
    setResult(null);
    setExtractionData(null);
  }, []);

  const reset = useCallback(() => {
    cancel();
  }, [cancel]);

  const start = useCallback(async (file: File) => {
    setPhase("uploading");
    setError(null);
    setProgress(5);
    setPagesProcessed(0);
    setTotalPages(0);
    setResult(null);
    setExtractionData(null);

    const controller = new AbortController();
    abortRef.current = controller;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${BACKEND_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: "Upload failed" }));
        throw new Error(err.error || `Server error ${res.status}`);
      }

      setProgress(20);
      setPhase("extracting");

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buf = "";
      let currentEvent = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;

        buf += decoder.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (currentEvent === "page" && data.page) {
                setPagesProcessed(data.page);
                const estimated = Math.min(80, 20 + data.page * 5);
                setProgress(estimated);
              } else if (currentEvent === "text-done" && data.pageCount) {
                setTotalPages(data.pageCount);
                setResult({
                  method: data.method,
                  pageCount: data.pageCount,
                  tookMs: data.tookMs,
                  documentId: data.documentId,
                });
              } else if (currentEvent === "extraction" && data.questions) {
                const mappedData: ExtractionReviewData = {
                  pdfMetadata: {
                    name: data.pdfName,
                    totalPages: data.pageCount,
                    totalQuestions: data.questionCount,
                    processingStatus: "completed",
                    uploadedAt: new Date().toISOString(),
                  },
                  pages: data.pages.map((p: { pageNumber: number }) => ({
                    pageNumber: p.pageNumber,
                    questionCount: data.questions.filter(
                      (q: { pageNumber: number }) => q.pageNumber === p.pageNumber
                    ).length,
                  })),
                  questions: data.questions.map((q: {
                    id: string;
                    questionNumber: number;
                    text: string;
                    type: string;
                    hasDiagram: boolean;
                    status: string;
                    pageNumber: number;
                  }) => ({
                    id: q.id,
                    questionNumber: q.questionNumber,
                    text: q.text,
                    type: q.type,
                    hasDiagram: q.hasDiagram,
                    status: "pending" as const,
                    pageNumber: q.pageNumber,
                  })),
                };
                setExtractionData(mappedData);
              }
            } catch {
              /* skip malformed */
            }
          }
        }
      }

      setProgress(90);
      setPhase("preparing");

      await new Promise((r) => setTimeout(r, 800));

      setProgress(100);
      setPhase("completed");
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setPhase("idle");
        setProgress(0);
        return;
      }
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
      setPhase("error");
    } finally {
      abortRef.current = null;
    }
  }, []);

  return { phase, error, progress, pagesProcessed, totalPages, result, extractionData, start, cancel, reset };
}
