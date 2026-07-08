import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import fs from "fs";
import path from "path";
import { processPDF } from "../services/documentProcessor.js";
import { processPDFWithPipeline } from "../services/pipelineBridge.js";
import { getDocumentDir } from "../services/pipelineBridge.js";

const documents = new Hono();

documents.post("/upload", async (c) => {
  const body = await c.req.parseBody();
  const file = body["file"];

  if (!file || !(file instanceof File)) {
    return c.json({ error: "No file provided" }, 400);
  }

  if (!file.name.endsWith(".pdf") && file.type !== "application/pdf") {
    return c.json({ error: "Only PDF files are supported" }, 400);
  }

  const buffer = Buffer.from(await file.arrayBuffer());

  const documentId = `doc-${Date.now()}`;
  const tempPath = `/tmp/${documentId}-${file.name}`;
  fs.writeFileSync(tempPath, buffer);

  return streamSSE(c, async (stream) => {
    const start = Date.now();

    try {
      const result = await processPDF(tempPath, async (page) => {
        await stream.writeSSE({
          event: "page",
          data: JSON.stringify({ page: page.page, text: page.text }),
        });
      });

      await stream.writeSSE({
        event: "text-done",
        data: JSON.stringify({
          method: result.method,
          pageCount: result.pageCount,
          tookMs: Date.now() - start,
          documentId,
        }),
      });

      const extractionResult = await processPDFWithPipeline(tempPath, documentId);

      await stream.writeSSE({
        event: "extraction",
        data: JSON.stringify(extractionResult),
      });

      await stream.writeSSE({
        event: "done",
        data: JSON.stringify({
          method: "content-pipeline",
          pageCount: extractionResult.pageCount,
          questionCount: extractionResult.questionCount,
          tookMs: Date.now() - start,
          documentId,
        }),
      });
    } finally {
      try { fs.unlinkSync(tempPath); } catch { /* ignore */ }
    }
  });
});

documents.get("/:id/pages/:pageNumber", async (c) => {
  const { id, pageNumber } = c.req.param();
  const docDir = getDocumentDir(id);
  if (!docDir) {
    return c.json({ error: "Document not found" }, 404);
  }
  const pageFile = path.join(docDir, "pages", `page_${pageNumber.padStart(3, "0")}.png`);

  if (!fs.existsSync(pageFile)) {
    return c.json({ error: "Page image not found" }, 404);
  }

  const img = fs.readFileSync(pageFile);
  return c.newResponse(img, 200, { "Content-Type": "image/png" });
});

documents.get("/:id/diagrams/:diagramId", async (c) => {
  const { id, diagramId } = c.req.param();
  const docDir = getDocumentDir(id);
  if (!docDir) {
    return c.json({ error: "Document not found" }, 404);
  }
  const digramFile = path.join(docDir, "diagrams", `${diagramId}.png`);

  if (!fs.existsSync(digramFile)) {
    return c.json({ error: "Diagram image not found" }, 404);
  }

  const img = fs.readFileSync(digramFile);
  return c.newResponse(img, 200, { "Content-Type": "image/png" });
});

export default documents;
