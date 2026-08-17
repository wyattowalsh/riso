# W5 CLOSE-COORD — live lock re-verify

Date: 2026-08-14
Wave: CLOSE-COORD
Branch: `main` · HEAD: `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
Cwd: `/Users/ww/dev/projects/riso` (`git rev-parse --show-toplevel`)
Exclusive writes this session: this file + `residuals/COORD.md`
Product edits (`template/copier.yml`, hooks, `template/prompts/**`): **0** (already fixed)
`samples/*/render/**` writes: **0**
No commit / tag / push / PyPI. No `render_matrix.py` started or killed.

## Status

**green** — COORD lock has no remaining P0/P1. Seeded items were re-read from live files and already match the contract. Dest leftover empty `openspec/` shells and missing `samples/default/render` stay PLATFORM-owned (official re-render). Do not add `openspec_extra: enabled` to sample answers.

## Seeded work (live)

| Item | Live | Verdict |
| --- | --- | --- |
| `EMPTY_SCAFFOLD_DIRS` includes `openspec` | `template/hooks/post_gen_project.py` L74; `cleanup_empty_scaffold_dirs` from `main()` L605 | **closed** — do not regress |
| Unrooted `_exclude` `"specs/"` | no item; comment L1894–1897 forbids it | **closed** |
| Unrooted `_exclude` `"README.md"` | no item; same comment (would drop `electron/README.md`, `openspec/specs/**`) | **closed** |
| Unrooted `config/` / `hooks/` / `samples/` / `prompts/` | no items | **closed** (parent closeout) |
| Container-adjacent excludes | wrapped `api_module != 'enabled'` for `riso-container-build.yml` + `riso-container-publish.yml` (L2054–2055) | **closed** — already live here; jinja empty-matrix omit is GATES, not this lock |
| `openspec_extra` default | `_defaults` + prompt default `disabled`; `_exclude` `openspec/` unless enabled (L2102) | **closed** |
| Sample answers `openspec_extra=enabled` | `rg` empty under `samples/**/copier-answers.yml` | **closed** — not added |
| Dest lucia choice | `saas_auth_provider` choices `clerk` \| `authjs` only | **closed** (wizard lucia is WEB) |
| Hooks apply-then-reject | pre_gen `_validate_removed_answer_keys`; post_gen `validate_removed_answer_keys` | **closed** |

`python/Makefile` exclude when `task_runner in ['just', 'none']` is unchanged. PAY-P0-linkcheck file is `template/files/python/Makefile.jinja` (PY / smoke), not this lock. Dual-runner ship of Makefile while `task_runner=just` would fight `test_task_runner_exclude_rules_by_mode`.

GATES container jinja already wraps `scan` / `publish-ghcr` when there is no python/node API language. COORD exclude stays `api_module != enabled` so rust/go-only APIs still receive the files (hadolint-only after GATES). Tightening the exclude to `{python,node}` would drop those dest workflows and fight the GATES design. Dest rust-api/go-api YAML remains stale until official re-render.

## Commands

```text
uv run pytest \
  tests/unit/hooks/test_post_gen_project.py::TestCleanupEmptyScaffoldDirs \
  tests/unit/hooks/test_pre_gen_project.py::TestValidateRemovedAnswerKeys \
  tests/unit/hooks/test_post_gen_project.py::TestLoadAnswers \
  tests/unit/test_task_runner_templates.py \
  -q -n 0 --tb=short
# 28 passed

uv run riso validate --answers-file samples/default/copier-answers.yml --json
# ok:true (warnings only _commit / _src_path)

uv run riso prompts --json
# openspec_extra default disabled; remap wording present
```

Live inspector (this session):

```text
openspec_in_empty_scaffold: True
openspec_extra_default: disabled
saas_auth_provider_choices: ['clerk', 'authjs']
unrooted_forbidden_items: []
has_unrooted_specs_item: False
has_unrooted_readme_item: False
has_openspec_exclude: True
container_build_rule: {% if api_module != 'enabled' %}...riso-container-build.yml{% endif %}
lucia_in_auth_choices: False
default_render_exists: False
leftover_openspec_dests: 25 empty shells (filecount 0)
```

## Not implemented here (foreign / dest)

| id | owner | why |
| --- | --- | --- |
| RES-OS-01 / dest empty `openspec/` | PLATFORM | Hook cleanup + exclude are live; dests predate them. Official `render-samples.sh` / `render_matrix.py` only. Never hand-rm dest dirs. |
| MS-P0-default-dest / fact-context-agents | PLATFORM | `samples/default/render` absent. Never hand-create dest. |
| PAY-P0-linkcheck | PY / PLATFORM | Recipe + smoke argv, not COORD exclude. |
| GATES-P0-container-* | GATES (jinja live) | Dest YAML stale until official re-render. |
| WIZ-P1-lucia-dest | WEB | Copier dest choices already clerk\|authjs. |
| NODE / PAY / MS payload P0/P1 | owning lanes | Files outside this lock. |

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 2 — this file, `residuals/COORD.md` |
| Product / hook / prompt edits | 0 |
| `samples/*/render/**` hand-edits | 0 |
| Lockfile / secret / commit / tag | 0 |
