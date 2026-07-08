import { Hono } from "hono";
import { authGuard } from "../middleware/auth.js";
import { db } from "../db/index.js";
import { modules as modulesTable, documents as documentsTable } from "../db/schema.js";
import { eq } from "drizzle-orm";
import { deleteFile } from "../services/storage.js";

const modules = new Hono();

modules.post("/", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const { name } = await c.req.json();
  if (!name || typeof name !== "string" || !name.trim()) {
    return c.json({ error: "Name is required" }, 400);
  }
  const [inserted] = await db.insert(modulesTable).values({
    userId: user.userId,
    name: name.trim(),
  }).returning({ id: modulesTable.id, name: modulesTable.name, createdAt: modulesTable.createdAt });
  return c.json(inserted, 201);
});

modules.get("/", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const rows = await db.select().from(modulesTable).where(eq(modulesTable.userId, user.userId)).orderBy(modulesTable.createdAt);

  const result = await Promise.all(rows.map(async (mod) => {
    const docs = await db.select({
      id: documentsTable.id,
      name: documentsTable.name,
      pageCount: documentsTable.pageCount,
      createdAt: documentsTable.createdAt,
    }).from(documentsTable).where(eq(documentsTable.moduleId, mod.id)).orderBy(documentsTable.createdAt);
    return { ...mod, documents: docs };
  }));

  return c.json(result);
});

modules.put("/:id", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const { name } = await c.req.json();
  if (!name || typeof name !== "string" || !name.trim()) {
    return c.json({ error: "Name is required" }, 400);
  }
  const [updated] = await db.update(modulesTable).set({ name: name.trim() }).where(eq(modulesTable.id, id)).returning({ id: modulesTable.id, name: modulesTable.name });
  if (!updated) return c.json({ error: "Not found" }, 404);
  return c.json(updated);
});

modules.delete("/:id", authGuard, async (c) => {
  const user = c.get("jwtPayload") as { userId: number; email: string; role: string };
  const id = Number(c.req.param("id"));
  const [mod] = await db.select().from(modulesTable).where(eq(modulesTable.id, id)).limit(1);
  if (!mod || mod.userId !== user.userId) return c.json({ error: "Not found" }, 404);

  const docs = await db.select().from(documentsTable).where(eq(documentsTable.moduleId, id));
  for (const doc of docs) {
    await deleteFile(doc.storagePath);
  }
  await db.delete(documentsTable).where(eq(documentsTable.moduleId, id)).execute();
  await db.delete(modulesTable).where(eq(modulesTable.id, id)).execute();

  return c.json({ success: true });
});

export default modules;
