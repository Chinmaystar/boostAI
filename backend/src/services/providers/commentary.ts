const COMMENTARY_PATTERNS = [
  /^(in\s+the\s+(image|picture|screenshot|photo|document|diagram)|the\s+(image|picture|screenshot|photo|document|diagram)\s+(presents|shows|depicts|contains|appears|displays|features|includes|provides|offers)|this\s+(image|picture|screenshot|photo|document|diagram|appears)|there\s+(is|are)|the\s+(layout|content|overall|page|document))/i,
  /^(based\s+on|looking\s+at|from\s+the|here['\u2019]s|here is|here are)/i,
  /^(the\s+user|i\s+need\s+to|let['\u2019]?s|let\s+me|first[,:]?\s+(let|i|we)|now[,:]?\s+(let|i|we|to))/i,
  /^(since\s+there|as\s+there|next[,:]?\s+|finally[,:]?\s+)/i,
  /^\d+[.)]\s+/,
  /^<\/(think|reason)>|^<think>/i,
];

const EXTRACTED_TEXT_MARKERS = [
  /the extracted text is:?$/im,
  /here is the extracted text:?$/im,
  /extracted text:?$/im,
  /output only the raw text:?$/im,
];

export function stripCommentary(text: string): string {
  for (const marker of EXTRACTED_TEXT_MARKERS) {
    const match = text.match(marker);
    if (match) {
      const after = text.slice(match.index! + match[0].length).trim();
      if (after) return after;
    }
  }

  const lines = text.split("\n");
  const filtered: string[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    if (COMMENTARY_PATTERNS.some((p) => p.test(trimmed))) continue;
    filtered.push(line);
  }
  return filtered.join("\n").trim();
}
