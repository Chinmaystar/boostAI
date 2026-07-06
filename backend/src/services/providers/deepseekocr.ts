import { config } from "../../config.js";
import { VisionProvider } from "./interface.js";

interface DeepSeekOCRResponse {
  choices: { message: { content: string } }[];
}

export class DeepSeekOCRProvider implements VisionProvider {
  async extractText(buffer: Buffer, mimeType: string, signal?: AbortSignal): Promise<string> {
    const base64Data = buffer.toString("base64");
    const dataUri = `data:${mimeType};base64,${base64Data}`;

    const body = {
      model: "deepseek-ocr-2",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "text",
              text: "<|grounding|>Convert the document to markdown.",
            },
            {
              type: "image_url",
              image_url: { url: dataUri },
            },
          ],
        },
      ],
      max_tokens: 8192,
      temperature: 0.0,
    };

    const res = await fetch(`${config.DEEPSEEK_OCR_URL}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${config.DEEPSEEK_OCR_API_KEY}`,
      },
      body: JSON.stringify(body),
      signal,
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`DeepSeek OCR API error ${res.status}: ${errText}`);
    }

    const data = (await res.json()) as DeepSeekOCRResponse;
    const raw = data.choices[0]?.message?.content || "";

    let cleaned = raw.trim();

    if (!cleaned) {
      console.log("[deepseek-ocr] empty response");
    }

    return cleaned;
  }
}
