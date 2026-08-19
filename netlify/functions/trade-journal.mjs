import { getStore } from "@netlify/blobs";
import { getUser, verifyRequestOrigin } from "@netlify/identity";

const STORE_NAME = "trade-journal";
const DATA_KEY = "journal.json";
const MAX_BODY_BYTES = 5_500_000;

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  },
});

const isAdmin = (user) => Boolean(user && (user.role === "admin" || user.roles?.includes("admin")));

function publicTrade(trade) {
  const copy = structuredClone(trade);
  delete copy.thought;
  delete copy.quantity;
  delete copy.stopPrice;
  delete copy.targetPrice;

  if (copy.privacy === "hideSymbol") copy.symbol = "銘柄非公開";
  if (copy.privacy !== "public") {
    delete copy.entryPrice;
    delete copy.exitPrice;
    delete copy.realizedPnl;
    copy.events = (copy.events || []).map((event) => {
      const item = { ...event };
      delete item.currentPrice;
      delete item.pnl;
      return item;
    });
  }

  return copy;
}

async function readTrades(store) {
  const value = await store.get(DATA_KEY, { type: "json", consistency: "strong" });
  return Array.isArray(value) ? value : [];
}

export default async (request) => {
  const store = getStore({ name: STORE_NAME, consistency: "strong" });
  const user = await getUser();
  const admin = isAdmin(user);

  if (request.method === "GET") {
    const trades = await readTrades(store);
    if (admin && new URL(request.url).searchParams.get("admin") === "1") {
      return json({ trades, admin: true });
    }
    return json({ trades: trades.filter((trade) => trade.published === true).map(publicTrade), admin: false });
  }

  if (request.method === "PUT") {
    if (!admin) return json({ error: "編集権限がありません。" }, 403);
    verifyRequestOrigin(request);
    const raw = await request.text();
    if (new TextEncoder().encode(raw).byteLength > MAX_BODY_BYTES) {
      return json({ error: "保存容量が大きすぎます。画像を減らして再度お試しください。" }, 413);
    }
    let body;
    try {
      body = JSON.parse(raw);
    } catch {
      return json({ error: "データ形式が正しくありません。" }, 400);
    }
    if (!Array.isArray(body.trades) || body.trades.length > 2000) {
      return json({ error: "記録データが正しくありません。" }, 400);
    }
    await store.setJSON(DATA_KEY, body.trades);
    return json({ ok: true, count: body.trades.length });
  }

  return json({ error: "Method not allowed" }, 405);
};

export const config = { path: "/api/trade-journal" };
