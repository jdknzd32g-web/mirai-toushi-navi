// Lightweight heuristics to extract topic and key point from markdown/txt

export type Extracted = {
  topic: string;
  point: string;
};

const headingRegex = /^(#{1,3})\s+(.+)/gm;

export function extract(text: string): Extracted {
  const lines = text.split(/\r?\n/);
  // find headings
  const headings: string[] = [];
  let m: RegExpExecArray | null;
  while ((m = headingRegex.exec(text))) {
    const h = sanitize(m[2]);
    if (h) headings.push(h);
  }
  // find conclusion-like lines
  const keywords = ['結論', 'まとめ', '要点', 'ポイント', '結語'];
  const concl = lines
    .map(sanitize)
    .filter(l => l.length > 0)
    .find(l => keywords.some(k => l.startsWith(k)) || /^(結論|まとめ)[:：]/.test(l));

  const firstHeading = headings[0] || guessTitle(lines) || '';
  const lastStrong = concl || findLastNonTrivialLine(lines) || '';
  return { topic: firstHeading, point: stripLeadKeywords(lastStrong) };
}

function stripLeadKeywords(s: string): string {
  return s.replace(/^(結論|まとめ|要点|ポイント)[:：\s]*/,'');
}

function guessTitle(lines: string[]): string | undefined {
  // First non-empty line that looks like a title
  return lines.map(sanitize).find(l => l.length >= 6 && l.length <= 60);
}

function findLastNonTrivialLine(lines: string[]): string | undefined {
  for (let i = lines.length - 1; i >= 0; i--) {
    const l = sanitize(lines[i]);
    if (!l) continue;
    if (l.length < 6) continue;
    return l;
  }
  return undefined;
}

export function sanitize(s: string): string {
  return s
    .replace(/[`*_>#\-\[\]\(\)]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function clampLen(s: string, min = 130, max = 140): { ok: boolean; len: number } {
  const len = [...s].length; // Unicode length
  return { ok: len >= min && len <= max, len };
}

