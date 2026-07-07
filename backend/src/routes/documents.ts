import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import { processPDF } from "../services/documentProcessor.js";
import { authGuard } from "../middleware/auth.js";
import { db } from "../db/index.js";
import { documents as documentsTable } from "../db/schema.js";
import { eq, and, isNull } from "drizzle-orm";
import fs from "fs";
import path from "path";

const documents = new Hono();

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
  const uploadDir = path.join(process.cwd(), "uploads", String(user.userId));
  fs.mkdirSync(uploadDir, { recursive: true });
  const storagePath = path.join(uploadDir, `${Date.now()}-${file.name}`);
  fs.writeFileSync(storagePath, buffer);

  return streamSSE(c, async (stream) => {
    const start = Date.now();
    const pages: { page: number; text: string }[] = [];

    try {
      const result = await processPDF(storagePath, async (page) => {
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
        event: "done",
        data: JSON.stringify({
          id: inserted.id,
          method: result.method,
          pageCount: result.pageCount,
          tookMs: Date.now() - start,
        }),
      });
    } finally {
      /* file kept permanently on disk */
    }
  });
});

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

documents.get("/:id/file", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const [doc] = await db.select().from(documentsTable).where(eq(documentsTable.id, id)).limit(1);
  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  const data = fs.readFileSync(doc.storagePath);
  return c.newResponse(data, 200, {
    "Content-Type": "application/pdf",
    "Content-Disposition": `inline; filename="${doc.name}"`,
  });
});

documents.delete("/:id", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const [doc] = await db.select().from(documentsTable).where(eq(documentsTable.id, id)).limit(1);
  if (!doc || doc.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  await db.delete(documentsTable).where(eq(documentsTable.id, id)).execute();
  try { fs.unlinkSync(doc.storagePath); } catch { /* file may already be gone */ }
  return c.json({ success: true });
});

export default documents;
