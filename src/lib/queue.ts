import path from 'path';
import { readJson, writeJson } from './fs.js';

export type QueueState = {
  queue: string[]; // file paths
};

export type PostedState = {
  posted: { date: string; file?: string; text: string; sig: string }[];
};

const QUEUE_PATH = 'posts/.queue.json';
const POSTED_PATH = 'posts/.posted.json';

export async function readQueue(): Promise<QueueState> {
  return readJson<QueueState>(QUEUE_PATH, { queue: [] });
}

export async function writeQueue(state: QueueState): Promise<void> {
  await writeJson(QUEUE_PATH, state);
}

export async function readPosted(): Promise<PostedState> {
  return readJson<PostedState>(POSTED_PATH, { posted: [] });
}

export async function appendPosted(item: { date: string; file?: string; text: string; sig: string }): Promise<void> {
  const s = await readPosted();
  s.posted.push(item);
  await writeJson(POSTED_PATH, s);
}

export function chooseFromQueue(queue: string[], fallback: string[]): string | undefined {
  if (queue.length > 0) return queue[0];
  return fallback[0];
}

export function dequeue(queue: string[], chosen?: string): string[] {
  if (!chosen) return queue;
  const p = path.normalize(chosen);
  return queue.filter(f => path.normalize(f) !== p);
}

