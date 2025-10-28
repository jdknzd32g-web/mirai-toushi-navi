#!/bin/bash
#
# ブログ記事自動作成スクリプト
#
# 使い方:
# ./scripts/auto-create-blog.sh ~/Desktop/テキストファイル.txt ~/Desktop/画像.jpg region4
#
# 引数:
# $1: テキストファイルのパス
# $2: 画像ファイルのパス
# $3: スラッグ（記事ID、例: region4）
# $4: カテゴリー（オプション、デフォルト: region）

set -e

if [ $# -lt 3 ]; then
  echo "エラー: 引数が不足しています"
  echo "使い方: $0 <テキストファイル> <画像ファイル> <スラッグ> [カテゴリー]"
  echo "例: $0 ~/Desktop/記事.txt ~/Desktop/画像.jpg region4"
  exit 1
fi

TEXT_FILE="$1"
IMAGE_FILE="$2"
SLUG="$3"
CATEGORY="${4:-region}"

echo "📝 ブログ記事を自動作成します..."
echo "   テキスト: $TEXT_FILE"
echo "   画像: $IMAGE_FILE"
echo "   スラッグ: $SLUG"
echo "   カテゴリー: $CATEGORY"
echo ""

# mirai-toushi-naviディレクトリに移動
cd "$(dirname "$0")/.."

# TypeScriptスクリプトを実行
npx tsx scripts/create-blog-post.ts \
  --text "$TEXT_FILE" \
  --image "$IMAGE_FILE" \
  --slug "$SLUG" \
  --category "$CATEGORY"

echo ""
echo "✅ ブログ記事の作成が完了しました！"
echo "   記事URL: https://eva-solution.netlify.app/blog/2025/$SLUG/$SLUG.html"
echo ""
echo "次のステップ:"
echo "1. blog/2025/$SLUG/$SLUG.html を確認"
echo "2. 必要に応じて内容を編集"
echo "3. git add . && git commit -m 'Add blog post: $SLUG'"
echo "4. git push"
