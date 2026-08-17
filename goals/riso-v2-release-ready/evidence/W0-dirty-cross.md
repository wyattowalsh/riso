# W0-T01f — Dirty-tree map, lane CROSS (CLI + WEB + PLATFORM + DOCS)

- Task: `W0-T01f`
- Wave: W0 / group W0A
- Lane: GOAL write (this file only). Product dirt classified to CLI / WEB / PLATFORM / DOCS.
- Filter: keep only paths matching `src/riso`, `web`, `scripts`, `docs`, `copier.yml`, `hooks`
- Verify: every matching dirty path listed; keep-or-drop vs `plan.md`; `samples/*/render/` write count = 0
- Status: **green**

## Repo identity

| Field | Value |
| --- | --- |
| CWD / toplevel | `/Users/ww/dev/projects/riso` (workspace root; `.git` present) |
| Branch | `main` (`.git/HEAD` → `ref: refs/heads/main`; porcelain: `main...origin/main [ahead 34, behind 1]`) |
| HEAD | `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` — `docs(docs): W4 ASSURANCE report and handoffs closeout` |
| `origin/main` | `6134759f78bdb2c8b160462d55e8b87b09d81291` (v1.2.11) — **behind** local `main` |
| Filter prefixes | `src/riso/**`, `web/**`, `scripts/**`, `docs/**`, `template/files/docs/**`, `template/copier.yml`, `template/hooks/**` |

Commands required by the mission: `git status --short` and `git diff --name-only`.

This worker has no shell (`run_terminal_command` not in the tool list). Porcelain is **not invented**: it is the live `git status --short` / `git diff --name-only` / `git ls-files --others --exclude-standard` capture from parent session `019ffa08-aa06-7ee2-ade5-356d0569fc81` (`terminal/call-26af77c5-f17a-446f-adc1-4733deddad6b-232.log`), unioned with the later `019ff9d6` `call-2b37110c-6d05-4683-9562-85580c0939cc-83.log` snapshot that adds the post-capture `scripts/lib/paths.py` and `src/riso/template/__init__.py` rows. Cross-checked against:

- `019ff9d6` `call-2da8d941-…-63.log` (`git status --short | head -200` + `git diff --stat` web block)
- current worktree `list_dir` / `read_file` / `grep` (this task)
- `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main`, `.git/logs/HEAD`

No git mutation. Branch not changed.

Filter notes:

- `docs` includes maintainer `docs/**` and generated-docs payload `template/files/docs/**` (DOCS exclusive root). It does **not** include `template/files/python/docs/**` (PY) or `template/files/node/docs/**` (NODE).
- `hooks` means COORD `template/hooks/**`, not `template/files/node/saas/hooks/**`.
- `template/files/AGENTS.md.jinja` / `CLAUDE.md.jinja` are DOCS-lane dirty but **outside** this path filter (noted under Adjacent, not counted).

## Matching dirty paths

`git status --short` ∩ filter. `git diff --name-only` = the `M` rows only (untracked excluded).

**Count: 56** matching dirty paths (49 `M` + 7 `??`). **0** `D`. **0** `copier.yml` / `template/hooks/**`.

### CLI — `src/riso/**` (2 `M`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `src/riso/cli/app.py` | **KEEP** — `--skip-post-gen` is in `_GLOBAL_FLAGS` (plan keep / CLI-T17). Do not strip. |
| `M` | `src/riso/template/__init__.py` | **KEEP** — `list_sample_variants` uses `os.scandir` as a context manager (plan keep). Added after the `26af77c5` snapshot; present in `2b37110c`. |

No other dirty `src/riso/**` rows. `generation_gates.py` still *reads* leftover `saas_auth` (W0-T02d / W1-C06) but that file is **not** in porcelain — committed leftover, not a dirty path.

### WEB — `web/**` (27 `M` + 2 `??`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `web/index.html` | **KEEP** — matching wizard polish |
| `M` | `web/src/__tests__/exportConfig.test.ts` | **KEEP** — WEB-T03 lockstep tests |
| `M` | `web/src/__tests__/setup.ts` | **KEEP** — test harness polish |
| `M` | `web/src/__tests__/store.test.ts` | **KEEP** — WEB-T05 store defaults |
| `??` | `web/src/__tests__/components/ProjectBasics.test.tsx` | **KEEP** — matching wizard test |
| `M` | `web/src/components/FieldHighlight.tsx` | **KEEP** — matching a11y/focus polish |
| `M` | `web/src/components/Header.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/Hero.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/SearchModal.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/SidebarSummary.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/Wizard.tsx` | **KEEP** — matching wizard polish |
| `M` | `web/src/components/modules/ModuleCard.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/modules/index.tsx` | **KEEP** — matching polish |
| `??` | `web/src/components/modules/Switch.tsx` | **KEEP** — named switches (existing wizard contract) |
| `M` | `web/src/components/presets/ConfettiEffect.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/presets/PresetCard.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/presets/PresetDetailDrawer.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/presets/SavePresetModal.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/AIToolsConfig.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/DocsConfig.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/ModulesConfig.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/ProjectBasics.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/ReviewOutput.tsx` | **KEEP** — matching polish |
| `M` | `web/src/components/steps/SaaSConfig.tsx` | **KEEP** — matching polish; remaps land in WEB-T01, not here |
| `M` | `web/src/components/warnings/DependencyWarnings.tsx` | **KEEP** — matching polish |
| `M` | `web/src/index.css` | **KEEP** — `--riso-ink` / `--riso-sand` theme polish |
| `M` | `web/src/lib/exportConfig.ts` | **KEEP** — WEB-T03; already emits canonical keys only (W0-T02c) |
| `M` | `web/src/lib/store.ts` | **KEEP** — WEB-T05; `task_runner=just`, no mypy (W0-T02c) |
| `M` | `web/src/lib/useFocusTrap.ts` | **KEEP** — matching a11y polish |

`web/src/lib/removedAnswerKeys.ts` is **not** dirty (committed 8-key prose SSOT). W1/WEB-T01 still add remap operators.

### PLATFORM — `scripts/**` (4 `M`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `scripts/ci/check_quality_parity.py` | **KEEP** — ladder / quality parity |
| `M` | `scripts/ci/generate_matrix_data.py` | **KEEP** — uses `iter_sample_answer_files` |
| `M` | `scripts/ci/render_matrix.py` | **KEEP** — blocking PL-T06 surface; discover via pruned walk. Do not residual. |
| `M` | `scripts/lib/paths.py` | **KEEP** — `iter_sample_answer_files` pruned `os.walk` (plan keep). Added after `26af77c5`; present in `2b37110c`. |

### DOCS — maintainer `docs/**` (12 `M` + 3 `??`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `docs/guides/ci-platforms.md` | **KEEP** — matching maintainer docs polish |
| `M` | `docs/guides/implementation-guide.md` | **KEEP** — matching polish |
| `M` | `docs/guides/quickstart.md` | **KEEP** — matching polish |
| `M` | `docs/guides/roadmap.md` | **KEEP** — matching polish |
| `M` | `docs/guides/testing-strategy.md` | **KEEP** — matching polish |
| `M` | `docs/guides/troubleshooting.md` | **KEEP** — matching polish |
| `M` | `docs/index.md` | **KEEP** — matching polish |
| `M` | `docs/modules/quality.md.jinja` | **KEEP** — ty/just lockstep |
| `M` | `docs/modules/workflows.md.jinja` | **KEEP** — matching polish |
| `M` | `docs/quickstart.md.jinja` | **KEEP** — matching polish |
| `M` | `docs/tools/index.md` | **KEEP** — matching polish |
| `??` | `docs/tools/ruff.md` | **KEEP** — canon tool page |
| `??` | `docs/tools/ty.md` | **KEEP** — ty not mypy |
| `??` | `docs/tools/uv.md` | **KEEP** — canon tool page |
| `M` | `docs/upgrade-guide.md.jinja` | **KEEP** — W4-D04 lockstep surface (keys/mise/OpenSpec extra still to land) |

`docs/guides/v2-migration.md` is **absent** (W4-D01 will add it). Not a dirty path.

### DOCS — generated payload `template/files/docs/**` (4 `M` + 2 `??`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| `M` | `template/files/docs/modules/codegen-scaffolding.md.jinja` | **KEEP** — ty wording lockstep |
| `M` | `template/files/docs/modules/docs-site.md.jinja` | **KEEP** — docs-module lockstep |
| `M` | `template/files/docs/modules/mcp.md.jinja` | **KEEP** — no `riso-mcp` reintro |
| `??` | `template/files/docs/modules/quality.md.jinja` | **KEEP** — generated quality module page |
| `??` | `template/files/docs/modules/workflows.md.jinja` | **KEEP** — generated workflows page |
| `M` | `template/files/docs/upgrade-guide.md.jinja` | **KEEP** — W4-D04 lockstep |

### COORD filter hits (`copier.yml`, `template/hooks/**`)

| Status | Path | keep-or-drop vs `plan.md` |
| --- | --- | --- |
| — | *(none)* | W1 owns `template/copier.yml` + `template/hooks/*.py` serially. Not currently dirty. |

## `git diff --name-only` ∩ filter

The 49 `M` paths above. Untracked `??` rows are status-only (not in `git diff --name-only`).

## plan.md keep / drop (CROSS)

| Item | Decision | Why |
| --- | --- | --- |
| `--skip-post-gen` in `_GLOBAL_FLAGS` | **KEEP** | `src/riso/cli/app.py`; CLI-T17 |
| `list_sample_variants` `os.scandir` CM | **KEEP** | `src/riso/template/__init__.py` |
| `iter_sample_answer_files` pruned walk | **KEEP** | `scripts/lib/paths.py`; used by `render_matrix.py` / `generate_matrix_data.py` |
| Wizard polish (focus/ARIA/theme/store) | **KEEP** | all `web/**` rows; WEB-T* remaps later, do not revert polish |
| Maintainer + generated docs polish | **KEEP** | `docs/**` + `template/files/docs/**`; W4 adds v2-migration / Unreleased 2.0.0 on top |
| SaaS Next/Remix flatten copies | **DROP** (not a CROSS write) | plan “stays dropped”; owned by SAAS |
| Maintainer `riso-mcp` | **DROP / forbid** | not in dirty CROSS set; do not reintroduce |
| Idle-gate pytest `.jinja` collection hack | **DROP** | not a CROSS path |
| Dual-path aliases after remap | **DROP** | remap contract; W1/W2 implement apply-then-reject |

## Adjacent dirty (out of this filter — do not own here)

| Path | Owner |
| --- | --- |
| `template/files/AGENTS.md.jinja`, `template/files/CLAUDE.md.jinja` | DOCS (`W4-D05`) |
| `tests/unit/test_cli/test_{argv_normalize,output,recopy,validate}.py` | CLI |
| `tests/unit/ci/test_{check_quality_parity,render_matrix}.py` + `??` ci tests | PLATFORM |
| `goals/**` | GOAL / other lane packages |
| `template/files/{python,node,electron,tauri,go,rust,saas,quality}/**` | payload lanes (see sibling W0-T01a–e) |

## `samples/*/render/` write count

**0**

- No `samples/**/render/**` row in `git status --short` or `git diff --name-only` (parent `26af77c5` capture).
- `.gitignore` has `samples/*/render/`.
- `samples/default/render/` is not present in the worktree.
- This task writes only `goals/riso-v2-release-ready/evidence/W0-dirty-cross.md`.

## SAAS runtime confirm (mission extra)

Not CROSS write roots. Existence only (W0-T01c / W2 SAAS-T01/T02):

| Path | Present |
| --- | --- |
| `template/files/node/saas/runtime/nextjs` | **yes** (`app/`, `docs/`, `lib/`, `middleware.ts.jinja`, `next.config.js.jinja`, …) |
| `template/files/node/saas/runtime/remix` | **yes** (`app/root.tsx.jinja`, `app/routes/comparison.tsx.jinja`, `remix.config.js.jinja`) |

Flatten copies at `node/saas` app root stay **dropped**.

## W2 / W4 follow-through (no W0 rewrite)

- CLI-T17 keep `--skip-post-gen`; CLI-T10+ apply-then-reject at call sites.
- WEB-T01 remap twin; WEB-T04/T05 already lean canonical in dirty store/export.
- PLATFORM keeps `render_matrix.py` / pruned sample walk; PL-T06 must run later (not residualable).
- W4-D01 still needs `docs/guides/v2-migration.md` (not dirty yet because it does not exist).

No CROSS residual. No files outside `goals/riso-v2-release-ready/evidence/W0-dirty-cross.md` written.
