#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "commit-msg: missing commit message file path" >&2
  exit 1
fi

commit_msg_file="$1"

run_commitlint() {
  if command -v pnpm >/dev/null 2>&1; then
    pnpm exec commitlint --edit "$commit_msg_file"
    return $?
  fi

  if command -v npx >/dev/null 2>&1 && [[ -f package.json ]]; then
    npx --no commitlint --edit "$commit_msg_file"
    return $?
  fi

  return 127
}

validate_conventional_fallback() {
  local subject
  subject="$(head -n1 "$commit_msg_file")"
  if [[ "$subject" =~ ^(feat|fix|docs|chore|refactor|test|perf|ci|build|revert|style)(\([[:alnum:]_./-]+\))?!?:[[:space:]]+.+ ]]; then
    return 0
  fi
  echo "commit-msg: message must follow conventional commits (type(scope): subject)" >&2
  echo "commit-msg: see https://www.conventionalcommits.org/" >&2
  return 1
}

status=0
run_commitlint || status=$?

if [[ $status -eq 0 ]]; then
  exit 0
fi

if [[ $status -eq 127 ]]; then
  echo "commit-msg: commitlint unavailable; using conventional commit pattern check." >&2
  validate_conventional_fallback
  exit $?
fi

exit "$status"