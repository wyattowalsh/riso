# W5-AUDIT-residuals — reconcile residual ledger vs live tree

- Task: `AUDIT-residuals`
- Wave: W5
- Lane: **residuals** (inspect-only; this file is the only write)
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-14
- Branch: `main` (`.git/HEAD` hook-denied; `.git/refs/heads/main` = `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`)
- `git rev-parse --show-toplevel`: not executed (no shell in this worker). Workspace + `.git/refs/heads/main` confirm this repo.
- `samples/*/render/**` writes: **0**
- Product-code edits: **0**
- `render_matrix.py` started or killed: **0**
- Status: **2 still-open implementation/process gaps** (`fact-refine-stop`, `fact-context-agents`) + **1 still-open dest leftover** (empty `openspec/`). Other residual rows are actually-closed-in-tree or stale-doc.

## Contract / method

Read-only. SSOT first: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/{CLI,GOAL,OPENSPEC,PLATFORM,SKILL}.md`. **Do not trust `ASSURANCE.md` or `W4-A01-fact-map.md` as live truth** — they disagree with each other and with the residual files.

Every residual below was re-read against live source / dests. No `uv run` / `just quality` this session (no shell). Historical command logs are cited only when the live file still matches.

Remap contract (not re-implemented): `apply_removed_key_remaps` then `reject_removed_answer_keys`. No dest overwrite. Idempotent. No dual-path after remap.

Plan refine-stop (`plan.md` L42, L291–296): two consecutive review passes with **no new P0/P1** **and** official ladder green. If a later pass finds P0/P1, reset the dry counter.

P0/P1 = still-open implementation or closeout-gate gaps.
`stale` = residual / ASSURANCE text already fixed in the live tree.
`closed` = verified-good residual row recorded as a strength.

## Residual inventory (five files, nine rows)

| Residual | File status | Live tree | Verdict |
| --- | --- | --- | --- |
| **CLI R1** JOIN leftover tests | **closed** | `saas_auth=firebase` fail-closed; apply-then-reject wired | **actually-closed-in-tree** |
| **GOAL R1** `fact-refine-stop` | **open** | No `W4-R01*` / `W4-R02*`; only `W4-R03-gates.md`; ladder not green; W5-AUDIT-gates recorded new P0s | **still-open** |
| **OPENSPEC R1** dest leftover empty `openspec/` | **open** (hook+test closed) | Hook list + unit test live; dests still have empty `openspec/` | **still-open dest** (impl actually-closed) |
| **OPENSPEC R2** unrooted `_exclude` | **closed** in template; dest proof pending | No `"specs/"` / `"README.md"` / `"config/"` / `"hooks/"` items | **actually-closed-in-tree** |
| **PLATFORM R1** `just quality` | format + JOIN closed in-tree; fresh log pending | JOIN tests flipped; `quality: lint typecheck test ssot`; W4-A01 format log stale | **actually-closed-in-tree**; ASSURANCE/`W4-A01-quality.txt` **stale-doc** |
| **PLATFORM R2** skill mirror | **closed** | 5 required files match `.agents` ↔ `.claude` | **actually-closed-in-tree** |
| **PLATFORM R3** official jinja argv | **closed** | `_expand_jinja_paths` walks dirs | **actually-closed-in-tree**; `W4-A01-ladder.txt` **stale-doc** |
| **PLATFORM R4** `just validate-agents` | **open** | `samples/default/render` absent | **still-open** |
| **SKILL R1** Claude mirror | **closed** | Same byte-identity as PLATFORM R2 | **actually-closed-in-tree** |

`render_matrix.py` is **not** residualed. `samples/metadata/render_matrix.json` is present (37 variants).

## 1. GOAL R1 — `fact-refine-stop` — still-open (P0)

Plan (`plan.md` L291–296, `plan.taskgraph.json` W4-R01 → W4-R02 → W4-R03):

- W4-R01: review pass 1 on payloads, CLI, wizard, docs, gates
- W4-R02: fix any P0/P1 from R01
- W4-R03: review pass 2 with **no new P0/P1**
- If R03 finds P0/P1, reset the dry counter

On-disk review evidence under `goals/riso-v2-release-ready/evidence/`:

| Expected | Present? |
| --- | --- |
| `W4-R01*` | **absent** (directory listing + `rg W4-R0[12]`) |
| `W4-R02*` | **absent** |
| `W4-R03-gates.md` | **present** (gates-only pass 2; 2026-08-13; “no new P0/P1” on that surface) |
| `W5-R01*` / `W5-R02*` / `W5-R03*` review pair | **absent** |

W5-AUDIT-* files are **lane audits**, not the required consecutive dry pair. They cannot close refine-stop:

- Only one historical review artifact exists (`W4-R03-gates.md`), and it covers **gates only**, not all five surfaces.
- `evidence/W5-AUDIT-gates.md` recorded **two new P0s** (container-build empty `needs: []` / empty `matrix.target`; container-publish empty matrix). That **resets** any dry counter.
- Residual `GOAL.md` R1 already states: on-disk review evidence is still only `W4-R03-gates.md`; write W5-R01/R02/R03 after the ladder.

Ladder is not fully green (see PLATFORM R4): `just validate-agents` still requires `samples/default/render`, which does not exist.

PAY-P0-06 (GHA/Circle/GitLab `tests/test_mcp.py` path) is **not** a live refine blocker. Residual `GOAL.md` R1 already records it fixed 2026-08-14. Live:

- `template/files/.github/workflows/riso-quality.yml.jinja` L77–82: `working-directory: python` + `uv run pytest tests/test_mcp.py -v`
- `template/files/.circleci/config.yml.jinja` L190–193: `cd python` then same pytest
- `template/files/.gitlab/.gitlab-ci.yml.jinja` L125–126: `cd python` then same pytest
- `template/files/python/tests/test_mcp.py.jinja` exists

`ASSURANCE.md` residual ledger L128 still narrates PAY-P0-06 + `just quality` red — **stale-doc**. `W4-A01-fact-map.md` L15 still scores 21/4 — **stale-doc** vs ASSURANCE exec (23/2) and vs this live read.

**Fix:** Official re-render of `default` (never hand-edit dests). Then write two consecutive dry review passes covering payloads, CLI, wizard, docs, **and** gates. If any new P0/P1 (including the W5-AUDIT-gates container P0s), fix and reset the pair. Capture a green official ladder. Do not invent a `v2.0.0` tag.

## 2. PLATFORM R4 — `fact-context-agents` — still-open (P1)

`justfile` L217–229 `validate-agents` always passes `--render-enabled samples/default/render` and smokes that dest.

Live `samples/default/` contains only `copier-answers.yml`, `smoke-results.json`, `baseline_quickstart_metrics.json`. **No `render/`**.

`scripts/ci/validate_agents_ecosystem.py` L100–106: missing dest → `render missing AGENTS.md: {render_dir}`.

Historical (still matches dest absence): `evidence/W4-A01-pytest-agents.txt` L2165–2174:

```text
agents-ecosystem: all checks passed          # template-only
Quality parity checks passed.
… --render-enabled samples/default/render …
agents-ecosystem: render missing AGENTS.md: samples/default/render
validate_agents_exit:1
```

`samples/metadata/render_matrix.json` L551–608: variant `default`, `render_status: failed` (Fumadocs NextConfig `output: string` smoke). Dest was later removed; it is not present now.

Contrast (present): `samples/cli-docs/render/AGENTS.md`, `samples/full-stack/render/AGENTS.md`, `samples/ai-tools-off/render/AGENTS.md`.

Context-sync is not the red half. Residual R4 is accurate.

**Fix:** Re-render `default` via `./scripts/render-samples.sh` / later `render_matrix.py` after the Fumadocs smoke is fixed. Never hand-create `samples/*/render/**`. Then re-run `just validate-agents`.

## 3. OPENSPEC R1 — dest leftover empty `openspec/` — still-open dest (P1)

Implementation is **actually-closed-in-tree**:

- `template/hooks/post_gen_project.py` L55–74: `EMPTY_SCAFFOLD_DIRS` includes `"openspec"`
- `tests/unit/hooks/test_post_gen_project.py` L281–292: `test_removes_empty_openspec_dir` asserts membership + rmdir
- `template/copier.yml` L95 default `openspec_extra: "disabled"`; L2102 excludes `openspec/` unless enabled
- No sample `copier-answers.yml` sets `openspec_extra` (rg empty) — extra stays default-off

Dests were copied **before** cleanup / exclude fix. Live leftover empty shells (directory exists, no children):

- `samples/api-python/render/openspec/`
- `samples/full-stack/render/openspec/`
- `samples/cli-docs/render/openspec/`
- `samples/ai-tools-off/render/openspec/`
- `samples/docs-fumadocs/render/openspec/`

Residual `OPENSPEC.md` R1 is **accurate** (open dest; hook+test closed). It does **not** flip `fact-openspec` (default extra is still `disabled`).

`W5-AUDIT-openspec.md` called residual R1 “stale because the list omitted `openspec`”. That description is **stale vs the current residual text**, which already records the hook+test as closed and keeps the dest leftover open.

**Fix:** Official re-render **with** post_gen (`./scripts/render-samples.sh`). Verify dest has **no** `openspec/` when extra is disabled. Do not hand-rm dest dirs. `--skip-post-gen` copies will still leave the shell.

## 4. OPENSPEC R2 — unrooted `_exclude` — actually-closed-in-tree

Live `template/copier.yml` L1893–1902: `_exclude` comment **forbids** unrooted `"README.md"`, `"specs/"`, `"config/"`, `"hooks/"`. Those items are **not** in the list. Grep for `^- "(README.md|specs/|config/|hooks/)"` in `copier.yml` is empty.

Template source still has `template/files/electron/README.md.jinja`. Official dest `samples/electron-app/render/electron/` has **no** `README.md` — dest age from the old unrooted exclude. Residual already says “closed in template; dest proof pending R1 re-render.” That dest proof is the same official re-render as R1, not a live template bug.

## 5. PLATFORM R1 — `just quality` — actually-closed-in-tree / stale-doc

Residual heading still says “not green”; status line says format + JOIN closed; wants a fresh `W5-LADDER-quality.txt`.

Live:

- `justfile` L98: `quality: lint typecheck test ssot`
- JOIN tests (see CLI R1) no longer assert remappable `api_tracks`
- `W4-A01-quality.txt` L4–12 (`Would reformat: 5 files`, exit 1) is a **historical** format-red
- `evidence/W5-PARENT-close.md` recorded `ruff format --check` clean on those five files

This session did not re-run `just quality`. No remaining implementation hole is visible in the residual’s named blockers. `ASSURANCE.md` residual ledger L132–134 still treats quality as red — **stale-doc**. `W4-A01-fact-map.md` L16 residual `fact-just-quality` is **stale-doc** vs residual `PLATFORM.md` R1 + parent close.

## 6. PLATFORM R3 — official jinja argv — actually-closed-in-tree / stale-doc

Live `scripts/ci/validate_jinja_templates.py`:

- Usage L8 / L91: `[file1.jinja] [dir ...]`
- `_expand_jinja_paths` L73–81: `is_dir()` → `rglob("*.jinja")`

Official ladder argv `template/files` therefore no longer hits `Not a file`. Residual R3 status is already `closed`. `W4-A01-ladder.txt` L4–7 and residual redacted log still quote the old error — **stale-doc**.

## 7. CLI R1 — JOIN leftover tests — actually-closed-in-tree

Live tests assert **unmapped leftover** `saas_auth=firebase`, not remappable `api_tracks`:

- `tests/integration/test_riso_cli.py` L52–64: `--data saas_auth=firebase` → exit 2, error contains `saas_auth`
- `tests/integration/test_control_plane_gates.py` L15–24: `data={"saas_auth": "firebase", ...}` → `ValidationFailedError`; worker not called

Apply-then-reject choke point: `src/riso/core/answers.py` L79–83 `apply_then_reject_removed_keys`. Generation gates: `src/riso/template/__init__.py` L538–544 apply then `validate_answers_for_generation`.

Residual `CLI.md` R1 is already **closed**. `ASSURANCE.md` L66–69 / L144–146 still lists the two JOIN tests as failing on remappable `api_tracks` — **stale-doc**. `W4-A01-pytest-agents.txt` L2159–2161 is a **stale log** vs live test source.

Do **not** restore reject-before-remap on remappable keys.

## 8. SKILL R1 / PLATFORM R2 — Claude skill mirror — actually-closed-in-tree

`scripts/ci/validate_release_readiness_skill.py` L13–18 `REQUIRED_FILES` (5): `SKILL.md`, `references/release-gates.md`, `references/task-graph.md`, `references/no-legacy-answer-policy.md`, `scripts/collect_release_evidence.py`. Validator compares `read_bytes()`.

Live reads (this audit): `.agents` and `.claude` `SKILL.md` (frontmatter `name: riso-release-readiness`; fail-closed leftover stop rule), `references/no-legacy-answer-policy.md` (8 keys; apply then reject; lucia fail-closes; no “Do not convert”), and `references/release-gates.md` (official jinja argv `template/files`) are identical across the pair.

`rg "Do not convert removed keys"` under `.agents` and `.claude`: **empty**.

Residual `SKILL.md` R1 and `PLATFORM.md` R2 are already **closed**. `evidence/W3-PL-T07-release.txt` (historical mirror mismatch) is **stale**.

## ASSURANCE / fact-map drift (stale-doc, not extra residuals)

| Claim | Where | Live |
| --- | --- | --- |
| facts 21/4 | `W4-A01-fact-map.md` | Residual files + this audit: 2 still-open facts (`refine-stop`, `context-agents`) |
| `just quality` / jinja / CLI-JOIN / PAY-P0-06 still red | `ASSURANCE.md` residual ledger | Residual files already closed those rows; live sources match closed |
| OPENSPEC R1/R2 still COORD-owned implementation | `ASSURANCE.md` L148–150 | Template/hook closed; dest leftover only (R1) |
| Refine-stop blocked by live PAY-P0-06 | `ASSURANCE.md` L128 | PAY-P0-06 templates + `test_mcp.py.jinja` fixed |

`fact-render-matrix` stays green / not residualed.

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 — this evidence file |
| `samples/*/render/**` hand-edits | 0 |
| Lockfile / secret / foreign-tree / product edits | 0 |
| `render_matrix.py` started or killed | 0 |
| Commit / tag / push / PyPI | 0 |

## Findings (JSON companion)

| id | severity | residual | live |
| --- | --- | --- | --- |
| RES-GOAL-01 | P0 | GOAL R1 | no W4-R01/R02; not two dry reviews; ladder not green |
| RES-PL-04 | P1 | PLATFORM R4 | `samples/default/render` missing |
| RES-OS-01 | P1 | OPENSPEC R1 | dest empty `openspec/` leftover |
| RES-PL-01 | stale | PLATFORM R1 / ASSURANCE | format+JOIN closed in tree |
| RES-PL-03 | stale | PLATFORM R3 / W4-A01-ladder | jinja walks dirs |
| RES-CLI-01 | closed | CLI R1 | leftover `saas_auth=firebase` |
| RES-OS-02 | closed | OPENSPEC R2 | unrooted `_exclude` gone |
| RES-SK-01 | closed | SKILL R1 / PLATFORM R2 | mirrors identical |
