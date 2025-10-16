import crypto from 'crypto';

export type PostedItem = { date: string; file?: string; text: string; sig: string };

export function signature(text: string): string {
  const norm = text
    .toLowerCase()
    .replace(/[\s\n]+/g, ' ')
    .replace(/[、，。,.!！?？]/g, '')
    .trim();
  return crypto.createHash('sha1').update(norm).digest('hex');
}

// Simple Jaccard on word set
export function jaccard(a: string, b: string): number {
  const A = new Set(tokens(a));
  const B = new Set(tokens(b));
  const inter = new Set([...A].filter(x => B.has(x)));
  const uni = new Set([...A, ...B]);
  return uni.size === 0 ? 0 : inter.size / uni.size;
}

function tokens(s: string): string[] {
  return s
    .toLowerCase()
    .replace(/[#\p{P}\p{S}]/gu, ' ')
    .split(/\s+/)
    .filter(Boolean);
}

export function tooSimilar(text: string, history: PostedItem[], threshold = 0.85): boolean {
  const recent = history.slice(-200); // safety cap
  return recent.some(h => jaccard(text, h.text) >= threshold);
}

