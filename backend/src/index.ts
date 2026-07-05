import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { cors } from "hono/cors";
import { config } from "./config.js";
import documents from "./routes/documents.js";

const app = new Hono();

app.use(
  "/api/*",
  cors({
    origin: ["http://localhost:3000", "http://127.0.0.1:3000"],
    allowMethods: ["POST", "GET", "OPTIONS"],
  })
);

app.route("/api/documents", documents);

app.onError((err, c) => {
  console.error("Unhandled error:", err);
  return c.json({ error: "Internal server error" }, 500);
});

console.log(`Server running on http://localhost:${config.PORT}`);
serve({ fetch: app.fetch, port: config.PORT });

warmUpOllama();

async function warmUpOllama() {
  if (config.VISION_PROVIDER !== "ollama") return;
  try {
    console.log(`[warmup] loading "${config.OLLAMA_MODEL}"...`);
    const res = await fetch(`${config.OLLAMA_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: config.OLLAMA_MODEL, prompt: ".", stream: false, keep_alive: "30m", options: { num_ctx: 16384 } }),
    });
    await res.text();
    console.log("[warmup] model ready");
  } catch (err) {
    console.warn("[warmup] failed:", (err as Error).message);
  }
}
