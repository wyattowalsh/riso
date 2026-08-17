# W5-R1 — Review pass 1, surface=gates (read-only)

- Task: `W5-R1`
- Wave: W5
- Lane: GOAL inspect-only; exclusive write is this file
- Surface: gates (`scripts/ci/**`, `scripts/lib/**`, `scripts/render-samples.sh`, `justfile`, `.github/workflows/**`, `.agents/skills/riso-release-readiness/**`, `.claude/skills/riso-release-readiness/**`, `samples/**/copier-answers.yml`)
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-14
- Prior review blobs (W4-R03-gates, W5-AUDIT-gates, W5-CLOSE-GATES, ASSURANCE): **untrusted**. Every keep/drop re-read in the live tree.
- `samples/*/render/**` writes: **0** (dests read only)
- Product-code edits: **0**
- `render_matrix.py`: not started, not killed
- Git: `.git/HEAD` denied by pre-tool hook. No `run_terminal_command` in this session. Cwd inferred from workspace + repo files (`justfile`, `scripts/ci/`, `goals/riso-v2-release-ready/`). No branch switch / stash / reset.

## Contract

Remap is apply-then-reject. `apply_removed_key_remaps` then leftover reject. No dest overwrite if dest is set. Idempotent. No dual-path aliases after remap. Generated Node floor stays 20. OpenSpec extra stays off by default. SaaS Next/Remix flatten stays reverted.

P0 = correctness / contract break. P1 = lockstep / DX. Empty lists only after inspection.

## Method

Live reads: remap twin, SSOT/jinja/skill validators, `render_matrix.py`, `render-samples.sh` (variant regex, bootstrap, sphinx smoke), `justfile` quality/ssot, maintainer workflows, both skill trees, all `samples/**/copier-answers.yml`, dest workflows/answers/smoke (read-only).

## Findings (this pass)

| id | sev | file | issue |
| --- | --- | --- | --- |
| GATES-P0-sphinx-make-linkcheck | **P0** | `scripts/render-samples.sh` | Sphinx smoke hardcodes `uv run make linkcheck` and never reads `task_runner`. Default just dests exclude `python/Makefile`. Live `docs-sphinx` + `changelog-python` docs smoke red. |
| GATES-P1-mise-trust | **P1** | `scripts/render-samples.sh` | Official dest writer never `mise trust`s generated `mise.toml` before `just`/`pnpm`. Always-on dest pins then fail-closed as untrusted. |

## Checklist

| Item | Verdict | Live evidence |
| --- | --- | --- |
| Remap twin apply-then-reject | **closed** | `scripts/lib/removed_answer_keys.py`: 8 `_FALLBACK_*` keys; `_write_dests` does not overwrite a set dest; apply drops old key; lucia **not** in `_SAAS_AUTH_PROVIDERS` (fail-closed). Hooks apply then leftover-reject. |
| 3-way SSOT + leftover sample scan | **closed** | `check_removed_key_ssot.py` EXPECTED_KEYS + CANONICAL_OPS; `scan_sample_answers_for_removed_keys()` via `iter_sample_answer_files()`. Exact leftover YAML-key `rg` on `samples/**/copier-answers.yml` and dest `.copier-answers.yml`: **empty**. |
| `just quality` / SSOT wiring | **closed** | `justfile:98` `quality: lint typecheck test ssot`; `justfile:102-104` SSOT command; `.github/workflows/quality.yml:274-275` cli-tests runs SSOT. |
| Jinja dir walk | **closed** | `validate_jinja_templates.py` `_expand_jinja_paths` `is_dir()` → `rglob("*.jinja")`. Tests: `tests/unit/ci/test_validate_jinja_templates.py`. |
| Nested variant names | **closed** | `render-samples.sh:593` `^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$`. GHA `validate-samples` uses `saas-starter/*`. Bootstrap fail-closed (`failed=1` → `render_variant` exit 1). |
| Skill mirrors + policy | **closed** | `.agents` ↔ `.claude` five required files match on read (SKILL, policy, release-gates, task-graph, collect script). Policy: 8 keys, apply then reject, lucia fail-closed, no “Do not convert”. Validator forbids that sentence. |
| Container empty `needs` / matrix | **closed** | Template omits `scan` / `publish-ghcr` unless python/node. Official dests `samples/rust-api/render` + `samples/go-api/render`: no `needs: []`, no live empty `matrix.target`. Tests: `tests/unit/test_github_workflow_templates.py`. |
| Sample answers 37 / no removed keys | **closed** | 26 top-level + 11 `saas-starter/*` = 37. Canonical dest keys only. `openspec_extra` absent in sample answers (dest default answers `openspec_extra: disabled`). |
| Generated Node floor 20 | **closed** | Dest `mise.toml` `node = "20"`; GHA sample jobs `node-version: "20"`; saas dest `NODE_VERSION: '20'`. Maintainer `release.yml` Node 22 is maintainer-only. |
| `riso-mcp` in scripts | **closed** | `rg riso-mcp` under `scripts/`: empty. |
| Sphinx official smoke vs just dest | **P0** | see below |
| Dest `mise.toml` trust | **P1** | see below |
| `render_matrix.py` JSON present | **not residualed** | `samples/metadata/render_matrix.json` has 37 variants (4 `ok` / 33 `failed`, `recorded_at` 2026-08-14T06:33:54Z). Script exits 1 on any `render_status=failed`. Failures are payload smoke + this P0/P1. |

## 1. P0 — Sphinx smoke ignores `task_runner`

`scripts/render-samples.sh` L169–173 (embedded smoke):

```python
elif docs_enabled and docs_framework == "sphinx-shibuya":
    docs_cwd = python_cwd
    if python_cwd and (python_cwd / "docs").exists():
        docs_command = ["uv", "run", "make", "linkcheck"]
```

`rg task_runner scripts/render-samples.sh` is **empty**. Smoke never consults the canonical runner.

Default `task_runner=just` excludes `python/Makefile` (`template/copier.yml` exclude; COORD). Both Sphinx sample answers omit `task_runner`:

- `samples/docs-sphinx/copier-answers.yml` L26–27 `docs_framework: sphinx-shibuya`
- `samples/changelog-python/copier-answers.yml` L28–29 same

Official dest `samples/docs-sphinx/render/.copier-answers.yml` L32 `task_runner: just`. Dest `python/justfile` L7–9 already has `linkcheck` (`uv run --group docs sphinx-build -b linkcheck …`). Dest has **no** `python/Makefile`. `quality_make` skipped (“Python quality scaffold not rendered”).

Live smoke:

- `samples/docs-sphinx/smoke-results.json` L21–32: `["uv","run","make","linkcheck"]` returncode 2, `make: *** No rule to make target 'linkcheck'. Stop.`
- `samples/changelog-python/smoke-results.json` L21–32: same command / same stderr.

This is a **gates** contract break: the official dest writer fails a valid just-only Sphinx dest. PY already shipped the just recipe; COORD still excludes Makefile. The smoke argv is PLATFORM/`render-samples.sh`.

**Fix (this lock):** honor `task_runner` — prefer `just linkcheck` when `python/justfile` exists, or invoke `uv run --group docs sphinx-build -b linkcheck docs dist/docs-linkcheck` from `python_cwd` (no make). Add a unit test that the sphinx command is not `make` when answers/default is just. Re-render via `./scripts/render-samples.sh` / `render_matrix.py`. Never hand-edit dest.

Foreign half stays `residuals/PY.md` R1 / COORD Makefile exclude.

## 2. P1 — dest `mise.toml` never trusted

Generated `mise.toml` is always-on (`samples/docs-sphinx/render/mise.toml` L1–7: `node = "20"`). `bootstrap_render_dependencies` and `just quality` smoke do not run `mise trust` on the dest pin.

Live:

- `samples/docs-sphinx/smoke-results.json` `quality_just` stderr: `mise ERROR error parsing config file: …/samples/docs-sphinx/render/mise.toml` / `Config files … are not trusted.`
- Same class as `residuals/GATES.md` R1 on official rust-api/go-api bootstrap (`pnpm` via untrusted dest mise).

`changelog-python` `quality_just` passed (already-trusted dest). Fail is environmental on freshly copied dests when mise is installed — which this maintainer repo ships.

**Fix:** after successful copy, `mise trust "${destination}/mise.toml"` when that file exists (or equivalent `MISE_TRUSTED_CONFIG_PATHS`). Do not hand-edit dest.

## Closed on this surface (do not re-open)

- Jinja official argv `template/files` directory walk.
- `just quality` includes `ssot`; GHA `cli-tests` runs `check_removed_key_ssot.py`.
- Skill `.agents` ↔ `.claude` mirror + 8-key apply-then-reject policy; no “Do not convert”.
- Nested `saas-starter/*` variant regex + GHA matrix paths.
- Bootstrap fail-closed in `render-samples.sh`.
- Container jinja + rust-api/go-api dests: no empty `needs` / empty publish matrix (commented dockerhub `target:` only).
- Sample + dest answers: zero leftover removed keys.
- Dest `samples/api-python/render/.github/workflows/riso-quality.yml` now `working-directory: python` + `uv --directory python` — `residuals/GATES.md` R4 is **stale**.

## Foreign / not elevated (not this surface’s P0/P1)

- Default fumadocs `/sitemap.xml` + `/robots.txt` + `output: export` — NODE payload. Gate reports the failure correctly. `residuals/GATES.md` R2.
- Circle/GitLab dest-root `uv sync` — `template/files/.circleci/config.yml.jinja:82`, `.gitlab/.gitlab-ci.yml.jinja:51,327`. COORD/payload. `residuals/GATES.md` R3.
- `references/task-graph.md` still names an `src/riso/mcp/**` lane. Policy forbids reintroducing `riso-mcp`. Same below-P1 note as W4-R03.
- `just ci-full` does not call `ssot`; `just quality` / `just ci` / GHA cli-tests do.
- `just clean-all` is `rm -rf samples/*/render` (does not clean nested `saas-starter/*/render`).
- Twin does not export `reject_removed_answer_keys`; hooks implement leftover reject after apply. Matches W1-M02.

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 — this evidence file |
| `samples/*/render/**` hand-edits | 0 |
| Lockfile / secret / foreign-tree / product edits | 0 |
| `render_matrix.py` started or killed | 0 |
