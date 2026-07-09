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

const CHUNK_SIZE = 2;

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

function chunkPages<T>(pages: T[]): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < pages.length; i += CHUNK_SIZE) {
    chunks.push(pages.slice(i, i + CHUNK_SIZE));
  }
  return chunks;
}

/* ─── Quiz (chunked) ─── */

export async function generateQuestions(
  pages: { page: number; text: string }[]
): Promise<QAItem[]> {
  const chunks = chunkPages(pages);
  const all: QAItem[] = [];

  for (const [i, chunk] of chunks.entries()) {
    try {
      const pageText = buildPageText(chunk);
      const systemPrompt = `You are an expert educator. Given textbook page text, generate questions and answers that test understanding of key concepts.

Return ONLY a valid JSON array (no markdown, no code fences). Each object:
{
  "questionNumber": number,
  "question": string,
  "answer": string,
  "type": "short-answer" | "explanation" | "proof" | "mcq"
}

Generate 3-6 questions for this section.`;

      const raw = await chatComplete([
        { role: "system", content: systemPrompt },
        { role: "user", content: pageText },
      ]);

      const parsed = cleanAndParse(raw);
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          all.push({
            questionNumber: all.length + 1,
            question: item.question || "",
            answer: item.answer || "",
            type: item.type || "short-answer",
          });
        }
      }
    } catch (err) {
      console.error(`[llm] quiz chunk ${i + 1}/${chunks.length} failed:`, (err as Error).message);
    }
  }

  if (all.length === 0) throw new Error("Failed to generate any questions");

  return all;
}

/* ─── Flashcards (chunked) ─── */

export async function generateFlashcards(
  pages: { page: number; text: string }[]
): Promise<Flashcard[]> {
  const chunks = chunkPages(pages);
  const all: Flashcard[] = [];

  for (const [i, chunk] of chunks.entries()) {
    try {
      const pageText = buildPageText(chunk);
      const systemPrompt = `You are an expert educator. Given textbook page text, create flashcards with key concepts on the front and clear explanations on the back.

Return ONLY a valid JSON array (no markdown, no code fences). Each object:
{
  "front": string,
  "back": string
}

Generate 3-5 flashcards for this section.`;

      const raw = await chatComplete([
        { role: "system", content: systemPrompt },
        { role: "user", content: pageText },
      ]);

      const parsed = cleanAndParse(raw);
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          if (item.front && item.back) {
            all.push({ front: item.front, back: item.back });
          }
        }
      }
    } catch (err) {
      console.error(`[llm] flashcard chunk ${i + 1}/${chunks.length} failed:`, (err as Error).message);
    }
  }

  if (all.length === 0) throw new Error("Failed to generate any flashcards");

  return all;
}

/* ─── Summary (chunked) ─── */

export async function generateSummary(
  pages: { page: number; text: string }[]
): Promise<SummaryResult> {
  const chunks = chunkPages(pages);

  if (chunks.length === 1) {
    try {
      return await generateSingleSummary(chunks[0]);
    } catch (err) {
      console.error(`[llm] summary generation failed:`, (err as Error).message);
      return { summary: "", keyPoints: [] };
    }
  }

  const partials: SummaryResult[] = [];
  for (const [i, chunk] of chunks.entries()) {
    try {
      partials.push(await generateSingleSummary(chunk));
    } catch (err) {
      console.error(`[llm] summary chunk ${i + 1}/${chunks.length} failed:`, (err as Error).message);
    }
  }

  if (partials.length === 0) {
    return { summary: "", keyPoints: [] };
  }

  if (partials.length === 1) {
    return partials[0];
  }

  try {
    const combinedText = partials
      .map((p, i) => `--- Part ${i + 1} ---\nSummary: ${p.summary}\nKey points:\n${p.keyPoints.map(k => `- ${k}`).join("\n")}`)
      .join("\n\n");

    const mergePrompt = `You are an expert educator. Below are summaries of different parts of a textbook document. Combine them into one coherent final summary.

Return ONLY a valid JSON object (no markdown, no code fences):
{
  "summary": string (2-3 paragraph consolidated summary),
  "keyPoints": string[] (5-10 consolidated bullet-point key takeaways)
}`;

    const raw = await chatComplete([
      { role: "system", content: mergePrompt },
      { role: "user", content: combinedText },
    ]);

    const parsed = cleanAndParse(raw);
    return {
      summary: parsed.summary || partials.map(p => p.summary).join("\n\n"),
      keyPoints: Array.isArray(parsed.keyPoints)
        ? parsed.keyPoints
        : partials.flatMap(p => p.keyPoints),
    };
  } catch (err) {
    console.error(`[llm] summary merge failed:`, (err as Error).message);
    return {
      summary: partials.map(p => p.summary).join("\n\n"),
      keyPoints: partials.flatMap(p => p.keyPoints),
    };
  }
}

async function generateSingleSummary(
  pages: { page: number; text: string }[]
): Promise<SummaryResult> {
  const pageText = buildPageText(pages);

  const systemPrompt = `You are an expert educator. Given textbook page text, write a concise summary covering the main points.

Return ONLY a valid JSON object (no markdown, no code fences):
{
  "summary": string (2-3 paragraph summary),
  "keyPoints": string[] (5-8 bullet-point key takeaways)
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
