import {
  acceptInvite,
  getUser,
  login,
  logout,
  recoverPassword,
  requestPasswordRecovery,
  verifyRequestOrigin,
} from "@netlify/identity";

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
  },
});

const session = (user) => ({
  authenticated: Boolean(user),
  admin: Boolean(user && (user.role === "admin" || user.roles?.includes("admin"))),
  email: user?.email || "",
});

export default async (request) => {
  if (request.method === "GET") return json(session(await getUser()));

  if (request.method === "POST") {
    verifyRequestOrigin(request);
    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "入力内容を確認してください。" }, 400);
    }
    if (body.action === "requestPasswordRecovery") {
      if (!body.email) return json({ error: "メールアドレスを入力してください。" }, 400);
      try {
        await requestPasswordRecovery(String(body.email));
        return json({ ok: true });
      } catch {
        return json({ error: "設定メールを送信できませんでした。時間をおいて再度お試しください。" }, 400);
      }
    }
    if (body.action === "recoverPassword") {
      if (!body.token || !body.password || String(body.password).length < 8) {
        return json({ error: "8文字以上の新しいパスワードを入力してください。" }, 400);
      }
      try {
        const user = await recoverPassword(String(body.token), String(body.password));
        const result = session(user);
        if (!result.admin) {
          await logout();
          return json({ error: "管理者として登録されていません。" }, 403);
        }
        return json(result);
      } catch {
        return json({ error: "パスワードを設定できませんでした。設定メールをもう一度送ってください。" }, 400);
      }
    }
    if (body.action === "acceptInvite") {
      if (!body.token || !body.password || String(body.password).length < 8) {
        return json({ error: "8文字以上のパスワードを入力してください。" }, 400);
      }
      try {
        const user = await acceptInvite(String(body.token), String(body.password));
        return json(session(user));
      } catch {
        return json({ error: "招待を完了できませんでした。招待リンクをもう一度開いてください。" }, 400);
      }
    }
    if (!body.email || !body.password) return json({ error: "メールアドレスとパスワードを入力してください。" }, 400);
    try {
      const user = await login(String(body.email), String(body.password));
      const result = session(user);
      if (!result.admin) {
        await logout();
        return json({ error: "管理者として登録されていません。" }, 403);
      }
      return json(result);
    } catch {
      return json({ error: "ログインできませんでした。入力内容を確認してください。" }, 401);
    }
  }

  if (request.method === "DELETE") {
    verifyRequestOrigin(request);
    await logout();
    return json({ ok: true });
  }

  return json({ error: "Method not allowed" }, 405);
};

export const config = { path: "/api/trade-journal-auth" };
