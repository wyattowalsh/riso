# Residual — Lane COORD (CLOSE-COORD)

## Summary

COORD lock (`template/copier.yml`, `template/hooks/pre_gen_project.py`, `template/hooks/post_gen_project.py`, `template/prompts/**`) has **no remaining P0/P1**. Closeout re-verified live files on 2026-08-14 and did not edit product code. Dest leftover empty `openspec/` shells and missing `samples/default/render` are PLATFORM official-re-render work.

## Residuals

### R1 — dest leftover empty `openspec/` — **OPEN** (lock closed)

| Field | Value |
| --- | --- |
| **task_id** | OS-T02 / RES-OS-01 |
| **owner** | PLATFORM |
| **status** | open (dest only) |
| **command** | `./scripts/render-samples.sh` or `uv run python scripts/ci/render_matrix.py` then `test ! -e samples/api-python/render/openspec` |
| **blocking reason** | `EMPTY_SCAFFOLD_DIRS` includes `openspec`; `_exclude` drops `openspec/` when extra is disabled; `test_removes_empty_openspec_dir` passes. 25 official dests still have empty `openspec/` shells (filecount 0). `samples/default/render` is absent. Must not hand-edit dests. |
| **redacted log** | `leftover_openspec_dests count=25`; `default_render_exists: False` |
| **fix** | Official re-render **with** post_gen. Do not add `openspec_extra: enabled` to sample answers. |
| **evidence** | `goals/riso-v2-release-ready/evidence/W5-CLOSE-COORD.md`; `residuals/OPENSPEC.md` R1 |

### R2 — unrooted `_exclude` — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | OS-T01-specs / W5 parent |
| **owner** | COORD |
| **status** | closed |
| **command** | inspect `template/copier.yml` `_exclude` |
| **blocking reason** | — |
| **redacted log** | no items `README.md`, `specs/`, `config/`, `hooks/`, `samples/`, `prompts/` |
| **fix** | none |
| **evidence** | `template/copier.yml` L1893–1897 + `_exclude` list |
