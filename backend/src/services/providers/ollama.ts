import fs from "fs";
import { config } from "../../config.js";
import { VisionProvider } from "./interface.js";
import { stripCommentary } from "./commentary.js";

interface OllamaMessage {
  role: string;
  content: string | OllamaContentPart[];
}

interface OllamaContentPart {
  type: "text" | "image_url";
  text?: string;
  image_url?: { url: string };
}

interface OllamaResponse {
  choices: { message: { content: string } }[];
}

export class OllamaVisionProvider implements VisionProvider {
  async extractText(buffer: Buffer, mimeType: string, signal?: AbortSignal): Promise<string> {
    const base64Data = buffer.toString("base64");
    const dataUri = `data:${mimeType};base64,${base64Data}`;

    const body = {
      model: config.OLLAMA_MODEL,
      keep_alive: "30m",
      max_tokens: 16384,
      options: { num_ctx: 16384 },
      messages: [
        {
          role: "system",
          content: "You are a text extraction engine. Output only the raw text visible in images. Never include reasoning, analysis, descriptions, or any text that was not in the image.",
        },
        {
          role: "user",
          content: [
            {
              type: "text",
              text: "Extract all visible text from this document image. Output only the exact words and characters that appear in the image, nothing else. Preserve line breaks.",
            },
            {
              type: "image_url",
              image_url: { url: dataUri },
            },
          ],
        },
      ],
      stream: false,
    };

    const res = await fetch(`${config.OLLAMA_URL}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal,
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Ollama API error ${res.status}: ${errText}`);
    }

    const data = (await res.json()) as OllamaResponse;
    const raw = data.choices[0]?.message?.content || "";
    let cleaned = stripCommentary(raw);

    if (!cleaned) {
      console.log("[ollama] empty response, retrying once...");
      const res2 = await fetch(`${config.OLLAMA_URL}/v1/chat/completions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...body, keep_alive: "30m", options: { num_ctx: 16384 } }),
        signal,
      });
      if (res2.ok) {
        const data2 = (await res2.json()) as OllamaResponse;
        const raw2 = data2.choices[0]?.message?.content || "";
        cleaned = stripCommentary(raw2);
      }
    }

    return cleaned;
  }
}
