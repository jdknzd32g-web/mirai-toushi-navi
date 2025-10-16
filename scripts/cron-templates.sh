#!/usr/bin/env bash
# Example crontab entries for local machine (JST). Adjust paths for your environment.
# Load Node and repo env, then run posting slots at 07:30 / 12:30 / 19:30 JST.

# 1) Find your Node and repo paths
# which node
# pwd  # at repo root

# 2) Edit and run: crontab -e
# Paste the following (replace /path/to/repo and /usr/local/bin/node/npm as needed).

# Environment
SHELL=/bin/zsh
PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin

# Morning 07:30 JST
30 7 * * * cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot morning --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1

# Noon 12:30 JST
30 12 * * * cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot noon --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1

# Evening 19:30 JST
30 19 * * * cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot evening --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1

# Dry-run variants (for testing)
# 25 7 * * *  cd /Users/satoshioka/Downloads/mirai-toushi-navi && npx tsx src/x-post.ts --slot morning --dry --root "/Users/satoshioka/YouTube project" >> logs/x-post.log 2>&1

