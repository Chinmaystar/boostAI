import { config } from "../config.js";
import { VisionProvider } from "./providers/interface.js";
import { GeminiVisionProvider } from "./providers/gemini.js";
import { OllamaVisionProvider } from "./providers/ollama.js";

const providers: Record<string, new () => VisionProvider> = {
  gemini: GeminiVisionProvider,
  ollama: OllamaVisionProvider,
};

export function createVisionProvider(): VisionProvider {
  const Ctor = providers[config.VISION_PROVIDER];
  if (!Ctor) {
    throw new Error(
      `Unknown vision provider: "${config.VISION_PROVIDER}". Use "gemini" or "ollama".`
    );
  }
  return new Ctor();
}
