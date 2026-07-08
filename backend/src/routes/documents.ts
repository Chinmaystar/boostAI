import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import fs from "fs";
import path from "path";
import { processPDF } from "../services/documentProcessor.js";
import { processPDFWithPipeline } from "../services/pipelineBridge.js";
import { getDocumentDir } from "../services/pipelineBridge.js";
import { authGuard } from "../middleware/auth.js";
import { db } from "../db/index.js";
import { documents as documentsTable } from "../db/schema.js";
import { eq, and, isNull } from "drizzle-orm";
import { uploadFile, getSignedUrl, getFileStream, deleteFile } from "../services/storage.js";
import { generateQuestions, generateFlashcards, generateSummary } from "../services/llm.js";

const documents = new Hono();

/* ─── Upload ─── */

documents.post("/upload", authGuard, async (c) => {
  const body = await c.req.parseBody();
  const file = body["file"];

  if (!file || !(file instanceof File)) {
    return c.json({ error: "No file provided" }, 400);
  }

  if (!file.name.endsWith(".pdf") && file.type !== "application/pdf") {
    return c.json({ error: "Only PDF files are supported" }, 400);
  }

  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const moduleIdStr = body["moduleId"];
  const moduleId = moduleIdStr ? Number(moduleIdStr) : null;

  const buffer = Buffer.from(await file.arrayBuffer());

  const documentId = `doc-${Date.now()}`;

  /* Upload to Firebase (or local fallback) */
  const storagePath = await uploadFile(buffer, user.userId, file.name);

  /* Write temp file for OCR processing, delete after */
  const tempFile = `/tmp/boostai-upload-${Date.now()}.pdf`;
  fs.writeFileSync(tempFile, buffer);

  return streamSSE(c, async (stream) => {
    const start = Date.now();
    const pages: { page: number; text: string }[] = [];

    try {
      const result = await processPDF(tempFile, async (page) => {
        pages.push(page);
        await stream.writeSSE({
          event: "page",
          data: JSON.stringify({ page: page.page, text: page.text }),
        });
      });

      const [inserted] = await db.insert(documentsTable).values({
        userId: user.userId,
        moduleId,
        name: file.name,
        pageCount: result.pageCount,
        storagePath,
        pages,
      }).returning({ id: documentsTable.id });

      await stream.writeSSE({
        event: "text-done",
        data: JSON.stringify({
          id: inserted.id,
          method: result.method,
          pageCount: result.pageCount,
          tookMs: Date.now() - start,
          documentId,
        }),
      });

      try {
        const extractionResult = await processPDFWithPipeline(tempFile, documentId);

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
      } catch (err) {
        console.error("[pipeline] extraction failed:", (err as Error).message);
        /* non-fatal: study tools will use LLM-generated content instead */
      }
    } finally {
      try { fs.unlinkSync(tempFile); } catch { /* ignore */ }
    }
  });
});

/* ─── List orphan docs ─── */

documents.get("/list", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const docs = await db.select({
    id: documentsTable.id,
    name: documentsTable.name,
    pageCount: documentsTable.pageCount,
    createdAt: documentsTable.createdAt,
  }).from(documentsTable).where(
    and(eq(documentsTable.userId, user.userId), isNull(documentsTable.moduleId))
  ).orderBy(documentsTable.createdAt);
  return c.json(docs);
});

/* ─── Serve PDF file ─── */

documents.get("/:id/file", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const [doc] = await db.select().from(documentsTable).where(eq(documentsTable.id, id)).limit(1);
  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  /* Try signed URL first (Supabase) */
  const signedUrl = await getSignedUrl(doc.storagePath);
  if (signedUrl) {
    return c.redirect(signedUrl, 302);
  }

  /* Fallback: proxy via backend */
  const { buffer } = await getFileStream(doc.storagePath);
  if (!buffer) return c.json({ error: "File not found" }, 404);

  return c.newResponse(new Uint8Array(buffer), 200, {
    "Content-Type": "application/pdf",
    "Content-Disposition": `inline; filename="${doc.name}"`,
  });
});

/* ─── Delete document ─── */

documents.delete("/:id", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const [doc] = await db.select().from(documentsTable).where(eq(documentsTable.id, id)).limit(1);
  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  await deleteFile(doc.storagePath);
  await db.delete(documentsTable).where(eq(documentsTable.id, id)).execute();
  return c.json({ success: true });
});

/* ─── Study content: generate ─── */

documents.post("/:id/generate", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const type = c.req.query("type") || "quiz";

  const [doc] = await db.select().from(documentsTable).where(eq(documentsTable.id, id)).limit(1);
  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);
  if (!doc.pages || doc.pages.length === 0) return c.json({ error: "Document has no extracted text" }, 400);

  let content: any;
  switch (type) {
    case "quiz":
      content = await generateQuestions(doc.pages);
      break;
    case "flashcards":
      content = await generateFlashcards(doc.pages);
      break;
    case "summary":
      content = await generateSummary(doc.pages);
      break;
    default:
      return c.json({ error: "Unknown type. Use quiz, flashcards, or summary" }, 400);
  }

  const existing = doc.studyContent || { quiz: [], flashcards: [], summary: null };
  (existing as any)[type] = content;

  await db.update(documentsTable)
    .set({ studyContent: existing })
    .where(eq(documentsTable.id, id))
    .execute();

  return c.json({ type, content });
});

/* ─── Study content: get ─── */

documents.get("/:id/study-content", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const type = c.req.query("type");

  const [doc] = await db.select({
    studyContent: documentsTable.studyContent,
    userId: documentsTable.userId,
  }).from(documentsTable).where(eq(documentsTable.id, id)).limit(1);

  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  if (type) {
    const content = (doc.studyContent as any)?.[type];
    if (!content) return c.json({ error: "Not generated yet" }, 404);
    return c.json({ type, content });
  }

  return c.json(doc.studyContent || { quiz: [], flashcards: [], summary: null });
});

/* ─── Pipeline page images ─── */

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
