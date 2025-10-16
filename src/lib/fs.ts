import { promises as fs } from 'fs';
import path from 'path';

export type CandidateFile = {
  file: string;
  mtimeMs: number;
  size: number;
};

const exts = new Set(['.md', '.mdx', '.txt']);

export async function exists(p: string): Promise<boolean> {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

export async function listContentRoots(cliRoot?: string): Promise<string[]> {
  if (cliRoot) return [cliRoot];
  const env = process.env.CONTENT_ROOTS?.split(',').map(s => s.trim()).filter(Boolean) || [];
  const defaults = ['/Users/satoshioka/YouTube project', '/Users/satoshioka/past_script'];
  const roots = env.length ? env : defaults;
  const out: string[] = [];
  for (const r of roots) {
    if (await exists(r)) out.push(r);
  }
  return out;
}

export async function* walk(dir: string): AsyncGenerator<string> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const e of entries) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) {
      yield* walk(p);
    } else {
      yield p;
    }
  }
}

export async function findCandidateFiles(root: string): Promise<CandidateFile[]> {
  const out: CandidateFile[] = [];
  for await (const f of walk(root)) {
    const ext = path.extname(f).toLowerCase();
    if (!exts.has(ext)) continue;
    const st = await fs.stat(f);
    out.push({ file: f, mtimeMs: st.mtimeMs, size: st.size });
  }
  // newest first
  out.sort((a, b) => b.mtimeMs - a.mtimeMs);
  return out;
}

export async function readText(file: string): Promise<string> {
  const buf = await fs.readFile(file);
  return buf.toString('utf8');
}

export async function ensureDir(p: string): Promise<void> {
  await fs.mkdir(p, { recursive: true });
}

export async function writeJson(p: string, data: unknown): Promise<void> {
  await ensureDir(path.dirname(p));
  await fs.writeFile(p, JSON.stringify(data, null, 2));
}

export async function readJson<T>(p: string, def: T): Promise<T> {
  try {
    const txt = await fs.readFile(p, 'utf8');
    return JSON.parse(txt) as T;
  } catch {
    return def;
  }
}

