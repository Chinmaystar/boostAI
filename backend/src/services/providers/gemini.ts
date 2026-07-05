import { GoogleGenerativeAI } from "@google/generative-ai";
import { config } from "../../config.js";
import { VisionProvider } from "./interface.js";
import { stripCommentary } from "./commentary.js";

export class GeminiVisionProvider implements VisionProvider {
  private genAI: GoogleGenerativeAI;

  constructor() {
    this.genAI = new GoogleGenerativeAI(config.GEMINI_API_KEY);
  }

  async extractText(buffer: Buffer, mimeType: string, _signal?: AbortSignal): Promise<string> {
    const model = this.genAI.getGenerativeModel({ model: "gemini-2.0-flash" });
    const base64Data = buffer.toString("base64");

    const result = await model.generateContent([
      {
        inlineData: {
          mimeType,
          data: base64Data,
        },
      },
      "Extract all visible text from this document. Return ONLY the words and numbers exactly as they appear. Do not describe the image. Do not summarize. Do not add explanations. Do not use introductory phrases. Just output the raw text content with line breaks preserved.",
    ]);

    return stripCommentary(result.response.text());
  }
}
