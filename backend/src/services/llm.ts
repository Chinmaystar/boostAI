import { config } from "../config.js";

export interface QAItem {
  questionNumber: number;
  question: string;
  answer: string;
  type: string;
}

export interface Flashcard {
  front: string;
  back: string;
}

export interface SummaryResult {
  summary: string;
  keyPoints: string[];
}

interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

async function chatComplete(
  messages: ChatMessage[],
  signal?: AbortSignal
): Promise<string> {
  const body = {
    model: config.DEEPSEEK_LLM_MODEL,
    messages,
    max_tokens: 8192,
    temperature: 0.3,
  };

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (config.DEEPSEEK_LLM_API_KEY) {
    headers["Authorization"] = `Bearer ${config.DEEPSEEK_LLM_API_KEY}`;
  }
  if (config.DEEPSEEK_LLM_URL.includes("openrouter.ai")) {
    headers["HTTP-Referer"] = "http://localhost:3000";
    headers["X-Title"] = "boostAI";
  }

  const baseUrl = config.DEEPSEEK_LLM_URL.replace(/\/+$/, "");
  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`LLM API error ${res.status}: ${errText}`);
  }

  const data = (await res.json()) as {
    choices: { message: { content: string } }[];
  };
  return data.choices[0]?.message?.content || "";
}

function cleanAndParse(raw: string): any {
  const cleaned = raw
    .replace(/^```(?:json)?\s*/gi, "")
    .replace(/\s*```\s*$/g, "")
    .trim();
  try {
    return JSON.parse(cleaned);
  } catch {
    /* try extracting top-level array/object via bracket matching */
    const arrayMatch = cleaned.match(/\[[\s\S]*\]/);
    if (arrayMatch) {
      try { return JSON.parse(arrayMatch[0]); } catch {}
    }
    const objMatch = cleaned.match(/\{[\s\S]*\}/);
    if (objMatch) {
      try { return JSON.parse(objMatch[0]); } catch {}
    }
    throw new Error("Failed to parse LLM response as JSON");
  }
}

function buildPageText(pages: { page: number; text: string }[]): string {
  return pages
    .map((p) => `--- Page ${p.page} ---\n${p.text}`)
    .join("\n\n");
}

export async function generateQuestions(
  pages: { page: number; text: string }[]
): Promise<QAItem[]> {
  const pageText = buildPageText(pages);

  const systemPrompt = `You are an expert educator. Given textbook page text, generate comprehensive questions and answers that test understanding of key concepts.

Return ONLY a valid JSON array (no markdown, no code fences). Each object:
{
  "questionNumber": number,
  "question": string,
  "answer": string,
  "type": "short-answer" | "explanation" | "proof" | "mcq"
}

Generate 5-10 questions covering the most important concepts.`;

  const raw = await chatComplete([
    { role: "system", content: systemPrompt },
    { role: "user", content: pageText },
  ]);

  const parsed = cleanAndParse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

export async function generateFlashcards(
  pages: { page: number; text: string }[]
): Promise<Flashcard[]> {
  const pageText = buildPageText(pages);

  const systemPrompt = `You are an expert educator. Given textbook page text, create flashcards with key concepts on the front and clear explanations on the back.

Return ONLY a valid JSON array (no markdown, no code fences). Each object:
{
  "front": string,
  "back": string
}

Generate 10-15 flashcards covering the most important terms and concepts.`;

  const raw = await chatComplete([
    { role: "system", content: systemPrompt },
    { role: "user", content: pageText },
  ]);

  const parsed = cleanAndParse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

export async function generateSummary(
  pages: { page: number; text: string }[]
): Promise<SummaryResult> {
  const pageText = buildPageText(pages);

  const systemPrompt = `You are an expert educator. Given textbook page text, write a concise summary covering the main points.

Return ONLY a valid JSON object (no markdown, no code fences):
{
  "summary": string (2-3 paragraph summary),
  "keyPoints": string[] (5-10 bullet-point key takeaways)
}`;

  const raw = await chatComplete([
    { role: "system", content: systemPrompt },
    { role: "user", content: pageText },
  ]);

  const parsed = cleanAndParse(raw);
  return {
    summary: parsed.summary || "",
    keyPoints: Array.isArray(parsed.keyPoints) ? parsed.keyPoints : [],
  };
}
