import { clampLen } from './text.js';

export type StyleOptions = {
  hashtags?: string[]; // up to 2
};

// Build two-sentence, desu/masu tone, simple metaphor/example.
export function buildPost(topic: string, point: string, opts: StyleOptions = {}): { text: string; len: number; } {
  const emojiSet = ['📈','🧠','💡','✅','📊','🌱','🛡️'];
  const pick = (i: number) => emojiSet[i % emojiSet.length];

  // Sentence 1: topic framing with easy metaphor
  const s1 = `${topic}は、地図とコンパスをそろえる作業だと思います${pick(0)}`;

  // Sentence 2: key point + example, desu/masu
  const s2base = normalizePoint(point);
  const s2 = `${s2base}。例えば毎月の積立は畑を耕すようにコツコツ続けます${pick(1)}`;

  const lines: string[] = [s1, '', s2];
  let text = lines.join('\n');

  // add up to 2 hashtags on a new line (optional)
  const tags = (opts.hashtags || []).slice(0, 2).map(t => t.startsWith('#') ? t : `#${t}`).join(' ');
  if (tags) {
    text += `\n\n${tags}`;
  }

  // try to fit 130-140 chars by trimming or slight padding
  let { ok, len } = clampLen(text);
  if (!ok) {
    if (len > 140) {
      // Hard trim from the end, preserve whole characters
      const arr = [...text];
      text = arr.slice(0, 140).join('');
      len = 140;
    } else if (len < 130) {
      // Add a short polite closer if room remains
      const closer = '\n\n詳しくは本文をご覧ください';
      const arr = [...text];
      const need = 130 - len;
      const add = [...closer].slice(0, Math.max(0, need)).join('');
      text = arr.join('') + add;
      len = [...text].length;
      if (len > 140) text = [...text].slice(0, 140).join('');
      len = [...text].length;
    }
  }
  return { text, len };
}

function normalizePoint(s: string): string {
  if (!s) return 'リスクを理解し分散と時間で備えます';
  // Make sure it ends with です/ます style lightly
  let out = s.replace(/[。.!?\s]+$/,'');
  if (!/[ですます]$/.test(out)) {
    out = out + 'です';
  }
  return out;
}

