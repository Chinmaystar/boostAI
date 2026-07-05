import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import { processPDF } from "../services/documentProcessor.js";

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

  const tempPath = `/tmp/${Date.now()}-${file.name}`;
  const fs = await import("fs");
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
        event: "done",
        data: JSON.stringify({
          method: result.method,
          pageCount: result.pageCount,
          tookMs: Date.now() - start,
        }),
      });
    } finally {
      try { fs.unlinkSync(tempPath); } catch { /* ignore */ }
    }
  });
});

export default documents;
