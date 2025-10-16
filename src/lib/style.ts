import { clampLen } from './text.js';

export type StyleOptions = {
  hashtags?: string[]; // up to 2
};

// Build two-sentence, desu/masu tone, simple metaphor/example.
export function buildPost(topic: string, point: string, opts: StyleOptions = {}): { text: string; len: number; } {
  const emojiSet = ['📈','🧠','💡','✅','📊','🌱','🛡️'];
  const pick = (i: number) => emojiSet[i % emojiSet.length];

  // Sentence 1: topic framing with easy metaphor (emoji at end)
  let s1 = `${topic}は、地図とコンパスをそろえる作業だと思います${pick(0)}`;

  // Sentence 2: key point + example, desu/masu (emoji at end)
  const s2point = normalizePoint(point);
  let s2core = `${s2point}。例えば毎月の積立は畑を耕すようにコツコツ続けます`;
  const s2emoji = pick(1);

  // Build initial text (two sentences, blank line between)
  const buildText = (hashtags: string[]) => {
    const s2 = s2core + s2emoji;
    const lines: string[] = [s1, '', s2];
    let t = lines.join('\n');
    if (hashtags.length) t += `\n\n${hashtags.join(' ')}`;
    return t;
  };

  const hashtags = (opts.hashtags || []).slice(0, 2).map(t => t.startsWith('#') ? t : `#${t}`);
  let text = buildText(hashtags);
  let { len } = clampLen(text);

  // Target 139-140; tune by inserting short polite fillers BEFORE the last emoji of s2
  const fillers = [
    ' めちゃくちゃ大切です',
    ' 無理なく続けます',
    ' じっくり積み上げます',
    ' 将来が楽になります',
    ' 不安に振り回されません',
    ' 継続がいちばんの近道です'
  ];

  const targetMin = 139;
  const targetMax = 140;

  const measure = () => {
    const t = buildText(hashtags);
    return { t, l: [...t].length };
  };

  // If short, add fillers gradually (keeping emoji at sentence end)
  if (len < targetMin) {
    for (const f of fillers) {
      const testCore = s2core + f;
      const prev = s2core;
      s2core = testCore; // try add
      const { t, l } = measure();
      if (l > targetMax) {
        s2core = prev; // revert if exceeded
        break;
      }
      text = t; len = l;
      if (len >= targetMin && len <= targetMax) break;
    }
    // If still short, attempt adding a second filler
    if (len < targetMin) {
      for (const f of fillers) {
        const testCore = s2core + f;
        const prev = s2core;
        s2core = testCore;
        const { t, l } = measure();
        if (l > targetMax) { s2core = prev; continue; }
        text = t; len = l;
        if (len >= targetMin && len <= targetMax) break;
      }
    }
  }

  // If slightly over, trim the core carefully (keep emoji at end)
  if (len > targetMax) {
    // Remove last filler words up to whitespace/punctuation
    s2core = s2core.replace(/( めちゃくちゃ大切です| 無理なく続けます| じっくり積み上げます| 将来が楽になります| 不安に振り回されません| 継続がいちばんの近道です)$/, '');
    const m = measure(); text = m.t; len = m.l;
  }

  // Final safety: clamp within 130-140
  const { ok } = clampLen(text);
  if (!ok) {
    if (len > 140) {
      text = [...text].slice(0, 140).join('');
    } else if (len < 130) {
      // add a tiny polite closer without adding another sentence
      const add = ' 少しずつ前進します';
      const prevCore = s2core;
      s2core = s2core + add;
      const m = measure();
      if (m.l <= 140) { text = m.t; len = m.l; }
      else { s2core = prevCore; }
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
