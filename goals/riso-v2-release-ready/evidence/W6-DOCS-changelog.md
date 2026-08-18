# W6-DOCS-changelog — DOCS-P1-01 dest-key lockstep

- Task: `DOCS-P1-01`
- Wave: W6
- Lane: DOCS
- Date: 2026-08-18T08:10:17Z
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87`
- Exclusive writes: `CHANGELOG.md`, this file
- `samples/*/render/**` writes: **0**
- Commit / tag / push / PyPI: **0**
- Git tags `v2.0.0` / `2.0.0`: **absent** (`git tag -l 'v2.0.0' '2.0.0'` empty)
- Status: **green** (`api_features` named as Copier dest key)

## Finding (from `W6-R03-docs.md`)

W6-R03 recorded CHANGELOG Unreleased 2.0.0 as teaching
`graphql_api_module` / `websocket_module` as derived Jinja flags without
naming the live Copier dest `api_features`.

Live re-read at start of this slice:

- Heading `## [Unreleased] 2.0.0` present (L9).
- No-tag sentence present (L11–12).
- Enable recipe already present from `a0f8aa7` (L58–59 before this edit):
  “Enable GraphQL/WebSocket with `api_features` (`graphql`, `websocket`)
  when `api_module=enabled`.”
- That line did **not** say `api_features` is the Copier dest key.
- Sibling operator copy `docs/guides/v2-migration.md` L50–53 names
  “the Copier prompt `api_features` (`graphql`, `websocket`) when
  `api_module=enabled`.”

## Fix

One dest-key sentence inserted next to the derived-flag line in
`CHANGELOG.md` L57–60. Flags stay **not** remapped (not added to the
8-row table). No version tag invented; heading stays
`## [Unreleased] 2.0.0`.

```text
`graphql_api_module` / `websocket_module` are derived Jinja flags, not removed
user keys. They are not remapped. `api_features` is the Copier dest key.
Enable GraphQL/WebSocket with `api_features` (`graphql`, `websocket`) when
`api_module=enabled`.
```

Lockstep source (read-only): `docs/guides/v2-migration.md` L50–53;
`template/copier.yml` L65–67 (legacy no-prompt defaults) and L354–365
(`api_features` multiselect `graphql` / `websocket` when
`api_module=enabled`).

## Verify

```text
git rev-parse --show-toplevel   # /Users/ww/dev/projects/riso
git rev-parse --abbrev-ref HEAD # main
git rev-parse HEAD              # f60fac8ea40e12fb0ad64f6d49ff6bf74b9a1b87
git tag -l 'v2.0.0' '2.0.0'     # empty
python3 -c 'from pathlib import Path; t=Path("CHANGELOG.md").read_text(); sec=t.split("## [Unreleased] 2.0.0",1)[1].split("## [1.2.11]",1)[0]; assert "api_features" in sec and "Copier dest key" in sec'
# heading: ## [Unreleased] 2.0.0
# dest-key sentence: present
# enable recipe: present
# flags not in remap table: ok
git status --short -- CHANGELOG.md goals/riso-v2-release-ready/evidence/W6-DOCS-changelog.md 'samples/*/render/**'
#  M CHANGELOG.md
# ?? goals/riso-v2-release-ready/evidence/W6-DOCS-changelog.md
```

## Not this slice

- No commit / tag / push / PyPI.
- `docs/guides/v2-migration.md`, `docs/changelog.md`,
  `template/files/docs/upgrade-guide.md.jinja`, and
  `template/files/AGENTS.md.jinja` were not edited (outside exclusive write).
- Historical pre-1.0 `## [Unreleased]` at the bottom of `CHANGELOG.md`
  was not rewritten.
