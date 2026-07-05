import fs from "fs";
import path from "path";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf.mjs";
import { checkTextQuality, containsMathContent } from "./textQualityChecker.js";
import { renderPDFPages, cleanupRenderFiles } from "./pdfRenderer.js";
import { createVisionProvider } from "./vision.js";
import { config } from "../config.js";

export interface ProcessResult {
  text: string;
  method: "pdf-parse" | "ollama" | "gemini";
  pageCount: number;
  pages: PageResult[];
}

export interface PageResult {
  page: number;
  text: string;
}

export async function processPDF(
  filePath: string,
  onPage?: (page: PageResult) => Promise<void>
): Promise<ProcessResult> {
  const buffer = fs.readFileSync(filePath);
  const providerLabel = config.VISION_PROVIDER as "ollama" | "gemini";

  const pdfjsResult = await tryPDFjs(buffer);

  if (!pdfjsResult) {
    console.log("pdfjs-dist failed entirely, falling back to vision provider for all pages...");
    const fullVision = await extractWithVision(buffer, providerLabel, null, onPage);
    return { ...fullVision, method: providerLabel };
  }

  const pagesToVision: number[] = [];
  const finalPages: PageResult[] = [];

  for (const page of pdfjsResult.pages) {
    const { acceptable, metrics } = checkTextQuality(page.text);
    const hasMath = containsMathContent(page.text);

    if (acceptable && !hasMath) {
      console.log(`[page ${page.page}] quality OK (alphaRatio=${metrics.alphaRatio.toFixed(2)} avgWordLen=${metrics.avgWordLen.toFixed(2)} chars=${metrics.totalChars})`);
      finalPages.push(page);
      if (onPage) await onPage(page);
    } else {
      console.log(`[page ${page.page}] needs vision (alphaRatio=${metrics.alphaRatio.toFixed(2)} avgWordLen=${metrics.avgWordLen.toFixed(2)} chars=${metrics.totalChars} hasMath=${hasMath})`);
      pagesToVision.push(page.page);
      finalPages.push(page);
    }
  }

  if (pagesToVision.length === 0) {
    return {
      text: pdfjsResult.fullText,
      method: "pdf-parse",
      pageCount: pdfjsResult.pageCount,
      pages: finalPages,
    };
  }

  console.log(`[vision] processing ${pagesToVision.length}/${pdfjsResult.pageCount} pages via ${providerLabel}...`);

  if (providerLabel === "gemini") {
    const visionResult = await extractWithVision(buffer, providerLabel, null, onPage);
    for (let i = 0; i < finalPages.length; i++) {
      if (pagesToVision.includes(finalPages[i].page)) {
        const vp = visionResult.pages.find((p) => p.page === finalPages[i].page);
        if (vp) finalPages[i].text = vp.text;
      }
    }
  } else {
    const visionTexts = await extractPagesWithVision(buffer, pagesToVision, onPage);
    for (let i = 0; i < finalPages.length; i++) {
      if (visionTexts[finalPages[i].page]) {
        finalPages[i].text = visionTexts[finalPages[i].page];
      }
    }
  }

  const mergedText = finalPages.map((p) => p.text).join("\n\n");

  return {
    text: mergedText,
    method: pagesToVision.length === pdfjsResult.pageCount ? providerLabel : "pdf-parse",
    pageCount: pdfjsResult.pageCount,
    pages: finalPages,
  };
}

async function tryPDFjs(
  buffer: Buffer
): Promise<{ fullText: string; pageCount: number; pages: PageResult[] } | null> {
  try {
    const uint8 = new Uint8Array(buffer);
    const loadingTask = pdfjsLib.getDocument({ data: uint8 });
    const doc = await loadingTask.promise;
    const pageCount = doc.numPages;
    const pages: PageResult[] = [];
    const textParts: string[] = [];

    for (let i = 1; i <= pageCount; i++) {
      const page = await doc.getPage(i);
      const textContent = await page.getTextContent();
      const pageText = textContent.items
        .map((item) => ("str" in item ? item.str : ""))
        .join(" ");
      pages.push({ page: i, text: pageText });
      textParts.push(pageText);
    }

    return { fullText: textParts.join("\n\n"), pageCount, pages };
  } catch (err) {
    console.warn("pdfjs-dist failed:", (err as Error).message);
    return null;
  }
}

async function extractPagesWithVision(
  buffer: Buffer,
  pageNumbers: number[],
  onPage?: (page: PageResult) => Promise<void>
): Promise<Record<number, string>> {
  const tempFile = `/tmp/boostai-vision-${Date.now()}.pdf`;
  fs.writeFileSync(tempFile, buffer);

  let pageImages: string[] = [];

  try {
    pageImages = renderPDFPages(tempFile);
    const provider = createVisionProvider();
    const results: Record<number, string> = {};

    for (let i = 0; i < pageImages.length; i++) {
      const pageNum = i + 1;
      if (!pageNumbers.includes(pageNum)) continue;

      const imgBuffer = fs.readFileSync(pageImages[i]);
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), config.VISION_TIMEOUT);
      try {
        const text = await provider.extractText(imgBuffer, "image/png", controller.signal);
        console.log(`[vision] page ${pageNum}/${pageImages.length} done (${text.length} chars)`);
        results[pageNum] = text;
        if (onPage) await onPage({ page: pageNum, text });
      } catch (err: any) {
        if (err.name === "AbortError") {
          throw new Error(`Vision provider timed out on page ${pageNum}`);
        }
        throw err;
      } finally {
        clearTimeout(timer);
      }
    }

    return results;
  } finally {
    try { fs.unlinkSync(tempFile); } catch { /* ignore */ }
    if (pageImages.length > 0) {
      cleanupRenderFiles(pageImages);
    }
  }
}

async function extractWithVision(
  buffer: Buffer,
  providerLabel: "ollama" | "gemini",
  _pageNumbers: number[] | null,
  onPage?: (page: PageResult) => Promise<void>
): Promise<{ text: string; pageCount: number; pages: PageResult[] }> {
  if (providerLabel === "gemini") {
    const provider = createVisionProvider();
    const text = await provider.extractText(buffer, "application/pdf");
    const pageCount = estimatePageCount(text);
    const pageTexts = splitIntoPages(text);
    const pages = pageTexts.map((t, i) => ({ page: i + 1, text: t }));
    for (const p of pages) {
      if (onPage) await onPage(p);
    }
    return { text, pageCount, pages };
  }

  return extractPagesWithVisionFull(buffer, onPage);
}

async function extractPagesWithVisionFull(
  buffer: Buffer,
  onPage?: (page: PageResult) => Promise<void>
): Promise<{ text: string; pageCount: number; pages: PageResult[] }> {
  const tempFile = `/tmp/boostai-vision-${Date.now()}.pdf`;
  fs.writeFileSync(tempFile, buffer);

  let pageImages: string[] = [];

  try {
    pageImages = renderPDFPages(tempFile);
    console.log(`[vision] rendered ${pageImages.length} pages: ${pageImages.map(p => path.basename(p)).join(", ")}`);

    const provider = createVisionProvider();
    const pageTexts: string[] = [];

    for (let i = 0; i < pageImages.length; i++) {
      const imgBuffer = fs.readFileSync(pageImages[i]);
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), config.VISION_TIMEOUT);
      try {
        const text = await provider.extractText(imgBuffer, "image/png", controller.signal);
        console.log(`[vision] page ${i + 1}/${pageImages.length} done (${text.length} chars)`);
        pageTexts.push(text);
        if (onPage) await onPage({ page: i + 1, text });
      } catch (err: any) {
        if (err.name === "AbortError") {
          throw new Error(`Vision provider timed out after 100s on page ${i + 1}`);
        }
        throw err;
      } finally {
        clearTimeout(timer);
      }
    }

    const text = pageTexts.join("\n\n");

    return {
      text,
      pageCount: pageTexts.length,
      pages: pageTexts.map((t, i) => ({ page: i + 1, text: t })),
    };
  } finally {
    try { fs.unlinkSync(tempFile); } catch { /* ignore */ }
    if (pageImages.length > 0) {
      cleanupRenderFiles(pageImages);
    }
  }
}

function estimatePageCount(text: string): number {
  const pageBreakMatches = text.match(/---\s*Page\s*\d+|---|\f/g);
  if (pageBreakMatches) {
    return pageBreakMatches.length + 1;
  }
  const lines = text.split("\n").length;
  return Math.max(1, Math.round(lines / 40));
}

function splitIntoPages(text: string): string[] {
  const pageBreaks = text.split(/(?:---\s*(?:Page\s*)?\d*\s*---|---|\f)/g);
  return pageBreaks.filter((p) => p.trim().length > 0);
}
