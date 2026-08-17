# Residual — Lane OPENSPEC (W5-CLOSE-GOAL-EVIDENCE)

## Summary

`openspec_extra` default remains `disabled`. `_exclude` still drops `openspec/` unless enabled. `EMPTY_SCAFFOLD_DIRS` includes `"openspec"`. Unrooted `_exclude` items are gone. Hook unit tests pass. Official **default** dest (2026-08-14 re-render) has **no** `openspec/`. Other official dests still have empty leftover shells.

This residual does **not** flip `fact-openspec`.

## Residuals

### R1 — dest leftover empty `openspec/` — **OPEN** (hook + test + default dest closed)

| Field | Value |
| --- | --- |
| **task_id** | OS-T02 / RES-OS-01 |
| **owner** | PLATFORM (official re-render) |
| **status** | open (implementation closed; default dest clean; other dests leftover) |
| **command** | official `./scripts/render-samples.sh` per leftover variant **with** post_gen, then `test ! -e samples/<v>/render/openspec` |
| **blocking reason** | Hook cleanup + unit test + Copier exclude are in-tree. Official default dest has no `openspec/` (`openspec_extra` disabled). 23 other dests still have empty shells (`children=0`): `ai-tools-off`, `api-monorepo`, `api-python`, `changelog-full-stack`, `changelog-monorepo`, `changelog-python`, `circleci-node`, `cli-docs`, `docs-docusaurus`, `docs-fumadocs`, `docs-fumadocs-full`, `docs-sphinx`, `electron-app`, `full-stack`, `gitlab-ci-python`, `go-cli`, `go-mcp`, `makefile-runner`, `mcp-typescript`, `rag-enabled`, `rust-cli`, `rust-mcp`, `tauri-app`. rust-api / go-api / default were re-rendered this wave and are not in that list. Must not hand-rm dest dirs. |
| **redacted log** | `TestCleanupEmptyScaffoldDirs` **3 passed**. `test ! -e samples/default/render/openspec` → absent. |
| **fix** | Official re-render remaining dests **with** post_gen. Do not add `openspec_extra: enabled` to sample answers. |
| **evidence** | `evidence/W5-CLOSE-dest-recheck.txt`; `evidence/W5-CLOSE-pytest-remap.txt`; `residuals/COORD.md` R1 |

### R2 — unrooted `_exclude` — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | OS-T01-specs |
| **owner** | COORD |
| **status** | closed |
| **command** | inspect `template/copier.yml` `_exclude` |
| **blocking reason** | — |
| **redacted log** | Forbidden unrooted `README.md` / `specs/` / `config/` / `hooks/` items are not in the list. |
| **fix** | none |
| **evidence** | `residuals/COORD.md` R2; `template/copier.yml` `_exclude` |
