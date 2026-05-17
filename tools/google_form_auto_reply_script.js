function sendAutoReply(e) {
  // フォームの回答を取得
  // ※ e.response が取得できない場合（テスト実行など）のエラーハンドリングが必要ですが、
  // トリガー実行を前提としています。
  
  var itemResponses = e.response.getItemResponses();
  var name = "";
  var email = "";

  // 質問のタイトルに合わせて変数に格納
  // ※Googleフォームの質問項目名と完全に一致させる必要があります
  for (var i = 0; i < itemResponses.length; i++) {
    var itemResponse = itemResponses[i];
    var title = itemResponse.getItem().getTitle();
    var answer = itemResponse.getResponse();

    // 柔軟にマッチング（「名前」「氏名」などが含まれていれば取得）
    if (title.indexOf("名前") !== -1 || title.indexOf("氏名") !== -1) {
      name = answer;
    } else if (title.indexOf("メール") !== -1) {
      email = answer;
    }
  }
  
  // 自動メール収集設定がオンの場合のバックアップ
  if (!email && e.response.getRespondentEmail()) {
    email = e.response.getRespondentEmail();
  }

  // メールアドレスがない場合は終了
  if (!email) {
    console.log("メールアドレスが見つかりませんでした");
    return;
  }

  // 送信元アドレスの設定
  // 注意: このアドレス(ryo@eva-solution.com)をGmail設定の「アカウントとインポート」>「名前」
  // にエイリアスとして追加し、確認コードによる認証を完了させておく必要があります。
  // 認証されていないアドレスを指定するとエラーになります。
  var fromAddress = "ryo@eva-solution.com"; 

  // 件名
  var subject = "【未来投資navi】個別相談お申し込みありがとうございます";

  // 本文
  var body = name + " 様\n\n"
    + "この度は「未来投資navi」の個別相談にお申し込みいただき、誠にありがとうございます。\n"
    + "お申し込み内容を確認いたしました。\n\n"
    + "今後の面談日時の調整についてご案内いたします。\n\n"
    + "■ 公式LINEにご登録済みの方\n"
    + "お手数ですが、下記のLステップより面談日時をご予約ください。\n"
    + "https://liff.line.me/2007337325-Wrnz1xdG?liff_id=2007337325-Wrnz1xdG&is=RUxdBxwY3C\n\n"
    + "■ 公式LINEにご登録されていない方\n"
    + "本メールへの返信にて、面談のご希望日時（第3希望まで）をお知らせください。\n"
    + "日程を調整の上、追ってご連絡させていただきます。\n\n"
    + "ご不明な点がございましたら、お気軽にお問い合わせください。\n\n"
    + "━━━━━━━━━━━━━━━━━━━\n\n"
    + "ファイナンシャルプランナー\n"
    + "未来投資navi  りょう\n\n"
    + "eva solution\n"
    + "本名：岡 賢志\n\n"
    + "住所：〒841-0005 佐賀県鳥栖市弥生が丘1-11-1 1103\n"
    + "メール : ryo@eva-solution.com\n"
    + "TEL：080-8387-6353\n"
    + "HP：https://eva-solution.netlify.app/\n\n"
    + "━━━━━━━━━━━━━━━━━━━";

  // メール送信オプション
  var options = {
    from: fromAddress,
    name: "未来投資navi（FPりょう）"
  };

  try {
    GmailApp.sendEmail(email, subject, body, options);
  } catch (e) {
    console.error("メール送信エラー: " + e.toString());
    // エイリアス設定がうまくいっていない場合のフォールバック（デフォルトアドレスで送信）
    // 件名に【転送】などを付けて区別することも可能
    // GmailApp.sendEmail(email, subject, body); 
  }
}