#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "commit-msg: missing commit message file path" >&2
  exit 1
fi

commit_msg_file="$1"

if command -v pnpm >/dev/null 2>&1; then
  pnpm exec commitlint --edit "$commit_msg_file"
  exit $?
fi

echo "commitlint skipped (pnpm not found); falling back to conventional-pre-commit if configured." >&2
exit 0
