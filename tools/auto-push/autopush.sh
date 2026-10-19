#!/usr/bin/env bash
set -euo pipefail

# Retired: automatic rebase/add-all and the 2025-only sitemap could overwrite
# reviewed sources. Keep this entrypoint inert for older clients and jobs.
echo "Automatic Git commit/push is disabled. Review changes and sync Git explicitly; see docs/daily-publishing.md." >&2
exit 1
