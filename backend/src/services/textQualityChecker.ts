export interface QualityMetrics {
  alphaRatio: number;
  avgWordLen: number;
  totalChars: number;
  wordCount: number;
}

export function checkTextQuality(text: string): {
  acceptable: boolean;
  metrics: QualityMetrics;
} {
  const t = text.trim();
  if (t.length === 0) {
    return { acceptable: false, metrics: { alphaRatio: 0, avgWordLen: 0, totalChars: 0, wordCount: 0 } };
  }

  const alphaCount = (t.match(/[a-zA-Z\s]/g) || []).length;
  const alphaRatio = alphaCount / t.length;

  const words = t.split(/\s+/).filter((w) => w.length > 0);
  if (words.length === 0) {
    return { acceptable: false, metrics: { alphaRatio, avgWordLen: 0, totalChars: t.length, wordCount: 0 } };
  }

  const avgWordLen =
    words.reduce((sum, w) => sum + w.length, 0) / words.length;

  const acceptable = alphaRatio >= 0.4 && avgWordLen >= 2.5;

  return {
    acceptable,
    metrics: { alphaRatio, avgWordLen, totalChars: t.length, wordCount: words.length },
  };
}

export function isTextQualityAcceptable(text: string): boolean {
  return checkTextQuality(text).acceptable;
}

const MATH_UNICODE = /[⎧⎨⎩⎰⎱∫∑√≈≠≤≥±∞∂∆∏∐−×÷πθλμσφωΩ]/;

export function containsMathContent(text: string): boolean {
  if (MATH_UNICODE.test(text)) return true;

  const nonSpace = text.replace(/\s/g, "");
  if (nonSpace.length === 0) return false;

  const digitCount = (text.match(/\d/g) || []).length;
  if (digitCount / nonSpace.length > 0.2) return true;

  return false;
}
