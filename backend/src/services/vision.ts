import { config } from "../config.js";
import { VisionProvider } from "./providers/interface.js";
import { GeminiVisionProvider } from "./providers/gemini.js";
import { OllamaVisionProvider } from "./providers/ollama.js";
import { DeepSeekOCRProvider } from "./providers/deepseekocr.js";

const providers: Record<string, new () => VisionProvider> = {
  gemini: GeminiVisionProvider,
  ollama: OllamaVisionProvider,
  "deepseek-ocr": DeepSeekOCRProvider,
};

export function createVisionProvider(): VisionProvider {
  const Ctor = providers[config.VISION_PROVIDER];
  if (!Ctor) {
    throw new Error(
      `Unknown vision provider: "${config.VISION_PROVIDER}". Use "gemini", "ollama", or "deepseek-ocr".`
    );
  }
  return new Ctor();
}
