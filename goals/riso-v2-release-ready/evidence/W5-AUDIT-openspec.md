# W5-AUDIT-openspec — read-only OpenSpec extra

- Task: `AUDIT-openspec`
- Wave: W5
- Lane: **openspec** (inspect-only)
- Write root: this file only
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` (no checkout / stash / reset; `.git/HEAD` hook-denied; `.git/refs/heads/main` = `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`)
- Date: 2026-08-14
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- Status: **no open P0/P1** after live-file inspection

## Contract checked

1. `openspec_extra` default **disabled**
2. `EMPTY_SCAFFOLD_DIRS` includes `openspec`
3. `template/copier.yml` `_exclude` must **not** use unrooted `specs/`
4. Unrooted `README.md` must **not** drop a required dest file
5. Enabled copy must include `openspec/specs/project/spec.md`

P0/P1 = still-open implementation gaps. `stale` = residual docs already fixed in tree. `closed` = verified-good.

## Method

Read-only. SSOT: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/*.md`. Live sources via `read_file` / `grep`. This session has **no shell** (`git rev-parse` / throwaway `riso copy` not run). Do not treat `ASSURANCE.md`, `residuals/OPENSPEC.md`, or `evidence/W2-OPENSPEC.md` as live truth.

Copier exclude matching (installed `copier/_main.py`): `match_exclude` is `PathSpec` gitignore against **dest** `dst_relpath`. Unrooted `README.md` / `specs/` would match any dest path with those names.

## 1. `openspec_extra` default disabled — closed

Live `template/copier.yml`:

| Surface | Value |
| --- | --- |
| `_defaults.openspec_extra` | `"disabled"` (L95) |
| prompt `openspec_extra.default` | `disabled` (L548) |
| choices | `disabled` / `enabled` |
| `_exclude` | `{% if openspec_extra != 'enabled' %}openspec/{% endif %}` (L2102) |

`samples/default/copier-answers.yml` omits the key (Copier default applies). `rg openspec_extra samples --glob '**/copier-answers.yml'` is empty — no sample variant invents `enabled`. Rendered dest answers (e.g. `samples/go-api/render/.copier-answers.yml` L41, `samples/docs-sphinx/render/.copier-answers.yml` L22) have `openspec_extra: disabled`.

Catalog `template/files/module_catalog.json.jinja`: `default_state: disabled`. Web store `web/src/lib/store.ts` L220: `openspec_extra: fromMatrix('openspec_extra', 'disabled')`. Prompts `template/prompts/v2.yml.jinja`: `default: disabled`. Docs/AGENTS/upgrade-guide all say default off.

## 2. `EMPTY_SCAFFOLD_DIRS` includes `openspec` — closed

Live `template/hooks/post_gen_project.py` L74: `"openspec"` is in `EMPTY_SCAFFOLD_DIRS`. `cleanup_empty_scaffold_dirs` is called from `main()` (L605).

Live hook test `tests/unit/hooks/test_post_gen_project.py::test_removes_empty_openspec_dir` (L281–292):

- asserts `"openspec" in EMPTY_SCAFFOLD_DIRS`
- empty dest `openspec/` is removed

`residuals/OPENSPEC.md` R1 still says the list does **not** include `openspec`. That residual is **stale**.

Official dests still show leftover empty `openspec/` shells (`samples/{go-api,electron-app,rust-api,ai-tools-off,mcp-typescript,tauri-app,docs-sphinx,cli-docs}/render/openspec/`). Those dests are pre-fix / pre-re-render artifacts (`openspec_extra: disabled`; filecount 0). Do **not** hand-edit. Next official `render-samples.sh` / `render_matrix.py` will let post_gen rmdir them. Not an implementation gap.

`--skip-post-gen` will still leave the empty shell (hook skipped). R1's verify command used `--skip-post-gen` and would stay red even after the hook fix. Correct verify is a copy **with** post_gen.

## 3. Unrooted `specs/` — stale (fixed)

Live `_exclude` has **no** `"specs/"` item. Only a comment (L1894–1897) forbids unrooted `"specs/"` because it would drop `openspec/specs/**`.

`rg` for `- "specs/"` / `- 'specs/'` under `template/` is empty.

Payload exists: `template/files/openspec/specs/project/spec.md.jinja`. Dest path after jinja strip: `openspec/specs/project/spec.md`. With unrooted `specs/` gone and the extra-gate empty when enabled, Copier will not skip that dest.

## 4. Unrooted `README.md` — closed (fixed this wave)

Live `_exclude` has **no** `"README.md"` item. Comment (L1894–1897) now forbids unrooted `"README.md"` because it dropped dest files such as `electron/README.md`.

W5 parent close (`evidence/W5-PARENT-close.md`) dropped unrooted `README.md`, `config/`, `hooks/`, `samples/`, `prompts/` from `_exclude`. `"specs/"` was already gone.

OpenSpec extra payload has **no** `openspec/README.md` (keeper name is `USAGE.md`). Required dest for this extra is `openspec/specs/project/spec.md`, not `README.md`. Unrooted `README.md` is gone, so it cannot drop that dest (or module `*/README.md.jinja` dests on the next official render).

Stale dests still lack `go/README.md`, `electron/README.md`, `rust/README.md`, `tauri/README.md`, `testing/README.md` even though those jinja sources exist. That is dest age vs the just-removed exclude, not a live `_exclude` item. Do not hand-edit dests.

## 5. Enabled copy includes `openspec/specs/project/spec.md` — closed (source)

Live payload tree:

```text
template/files/openspec/
├── AGENTS.md.jinja
├── USAGE.md.jinja
├── config.yaml.jinja
├── changes/USAGE.md.jinja
├── changes/archive/USAGE.md.jinja
└── specs/project/spec.md.jinja
```

Gate when enabled: `_exclude` `openspec/` rule renders to empty string (same pattern as other conditional excludes; dest trees still copy files). No `specs/` pattern remains.

W2 throwaway dest (`evidence/W2-OPENSPEC-dest-trees.txt`) is **stale**: it predates the `specs/` removal and records `MISSING openspec/specs/project/spec.md`. Do not treat that dest tree as live.

This session did not run a throwaway `riso copy` (no shell). Source-level proof: dest `openspec/specs/project/spec.md` is not matched by any live `_exclude` when `openspec_extra=enabled`. Official sample dests are all extra-disabled, so they cannot prove the enabled path.

## Residual disposition

| Residual | Live tree | Verdict |
| --- | --- | --- |
| `residuals/OPENSPEC.md` R1 (`EMPTY_SCAFFOLD_DIRS` missing `openspec`) | L74 + `test_removes_empty_openspec_dir` | **stale** |
| `residuals/OPENSPEC.md` R2 (unrooted `"specs/"` + `"README.md"`) | neither item in `_exclude`; comment forbids both | **stale** |
| `ASSURANCE.md` “OPENSPEC R1/R2 still COORD-owned” | implementation closed | **stale narrative** |

`fact-openspec` (extra default off) remains true.

## Path lock

Exclusive write: this evidence file. No product code, no residuals rewrite, no dest edits, no lockfiles, no commit/tag/push/PyPI.

## Findings summary

No still-open P0/P1. Closed contract items recorded below; R1/R2 residual docs are stale.
