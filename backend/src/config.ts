import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  PORT: z.coerce.number().default(3001),
  GEMINI_API_KEY: z.string().default(""),
  VISION_PROVIDER: z.enum(["gemini", "ollama", "deepseek-ocr"]).default("ollama"),
  OLLAMA_URL: z.string().default("http://localhost:11434"),
  OLLAMA_MODEL: z.string().default("qwen3-vl:2b"),
  DEEPSEEK_OCR_URL: z.string().default("https://deepseek-ocr-v2-demo.vercel.app/api/v1"),
  DEEPSEEK_OCR_API_KEY: z.string().default("whale"),
  VISION_TIMEOUT: z.coerce.number().default(300_000),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("Invalid environment variables:", parsed.error.flatten().fieldErrors);
  process.exit(1);
}

export const config = parsed.data;
