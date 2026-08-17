# W5-AUDIT — surface=gates (read-only)

- Task: `W5-AUDIT-gates`
- Wave: W5
- Lane: GOAL inspect-only; exclusive write is this file
- Surface: gates (`scripts/ci/**`, `justfile` quality/ssot, release-readiness skill + Claude mirror, generated container workflow jinja)
- Repo: `/Users/ww/dev/projects/riso`
- Date: 2026-08-14
- `samples/*/render/**` writes: **0** (dest workflows read only)
- Product code edits: **0**
- Status: **2 open P0** on container workflows; other named gates verified in tree

## Contract / method

Remap is apply-then-reject. `render_matrix.py` was not started or killed. No commit / tag / push / PyPI.

SSOT read first: `goals/riso-v2-release-ready/{goal,facts,plan,ASSURANCE}.md` and `residuals/{PLATFORM,SKILL,GOAL,CLI,OPENSPEC}.md`. ASSURANCE / W3–W4 logs are untrusted; every claim below is re-read from live files.

`.git/HEAD` is denied by the pre-tool hook. Workspace path matches prior W4-A01 evidence (`main`, HEAD `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`). This session has no shell; validators were not re-executed. Verdicts are from live source + official dest reads.

## Checklist

| Item | Verdict | Live evidence |
| --- | --- | --- |
| `validate_jinja_templates.py` directory walk | **closed** | `_expand_jinja_paths` `is_dir()` → `rglob("*.jinja")` |
| `check_removed_key_ssot.py` 3-way + leftover scan | **closed** | 8 keys + ops; `scan_sample_answers_for_removed_keys` |
| `just quality` / `ssot` wiring | **closed** | `quality: lint typecheck test ssot`; GHA cli-tests runs SSOT |
| Skill mirrors byte-identical | **closed** | 5/5 `.agents` ↔ `.claude` files match; no “Do not convert” |
| `validate_release_readiness_skill.py` | **closed** | byte compare + 8-key apply-then-reject policy contract |
| `riso-container-build.yml.jinja` scan `needs` | **P0** | dest `needs: []` + empty `matrix.target` |
| `riso-container-publish.yml.jinja` matrix | **P0** | dest empty `matrix.target` when no python/node |

## 1. Jinja directory walk — closed

`scripts/ci/validate_jinja_templates.py`:

- Usage line: `[file1.jinja] [dir ...]`.
- `_expand_jinja_paths` (L73–81): directories expand via `sorted(file_path.rglob("*.jinja"))`; explicit files stay as-is.
- Official ladder argv `template/files` therefore no longer hits `Not a file`.

Stale contrary logs (do not treat as live red):

- `evidence/W4-A01-ladder.txt` L4–7 (`template/files: Not a file`)
- `residuals/PLATFORM.md` R3 redacted log / blocking reason (status already `closed`)

Pre-commit still passes individual `*.jinja` paths (`pass_filenames: true`). That is compatible with the walk. No unit test asserts directory expansion (`tests/test_precommit.py` only compile-checks the script). Below P1.

## 2. `check_removed_key_ssot.py` — closed

Live script checks:

- 8 `EXPECTED_KEYS` + `CANONICAL_OPS` (wrap-list / derive / rename / split / rename-bool)
- core `src/riso/core/removed_answer_keys.py`
- twin `scripts/lib/removed_answer_keys.py` `_FALLBACK_*` (not packaged re-exports)
- web `web/src/lib/removedAnswerKeys.ts` (static parse)
- `plan.taskgraph.json` `remap_keys`
- `scan_sample_answers_for_removed_keys()` via `iter_sample_answer_files()`

Three-way tables inspected: same 8 keys and same `(old, new_keys, action)` rows. Tests: `tests/unit/ci/test_check_removed_key_ssot.py` (repo 3-way, leftover fixture detect).

## 3. `just quality` / `ssot` wiring — closed

```text
justfile:98   quality: lint typecheck test ssot
justfile:102  ssot: uv run python scripts/ci/check_removed_key_ssot.py
justfile:108  ci-ssot: ssot
justfile:233  ci: install quality   # inherits ssot
.github/workflows/quality.yml:274-275  cli-tests job runs check_removed_key_ssot.py
```

`just ci-full` still does **not** call `ssot` (only `run_quality_suite.py` + coverage pytest). Same note as W4-R03; not elevated.

This session did not re-run `just quality`. `evidence/W4-A01-quality.txt` is a historical format-red. `residuals/PLATFORM.md` R1 status is `closed` (parent closeout). Wiring is the gate under audit; live suite is not re-verified here.

## 4. Skill mirrors + validator — closed

Required set (validator `REQUIRED_FILES`):

| Relative path | `.agents` ↔ `.claude` |
| --- | --- |
| `SKILL.md` | identical (frontmatter `name: riso-release-readiness`) |
| `references/no-legacy-answer-policy.md` | identical; 8 keys; apply then reject; lucia fail-closed |
| `references/release-gates.md` | identical; lists SSOT + jinja `template/files` + leftover scan |
| `references/task-graph.md` | identical |
| `scripts/collect_release_evidence.py` | identical |

`rg "Do not convert removed keys"` under `.agents` and `.claude`: **empty**.

`scripts/ci/validate_release_readiness_skill.py`:

- file-set equality
- `read_bytes()` identity
- `validate_policy_contract`: all 8 keys; phrases `apply_removed_key_remaps`, `reject_removed_answer_keys`, `apply then reject`; forbids the exact do-not-convert sentence

Tests include `test_repository_skill_mirror_is_valid` and `test_validate_policy_contract_rejects_do_not_convert`.

`residuals/SKILL.md` R1 and `residuals/PLATFORM.md` R2 are already marked closed. `evidence/W3-PL-T07-release.txt` (mirror mismatch, exit 1) is **stale**.

`task-graph.md` still names an `src/riso/mcp/**` lane. Policy already forbids reintroducing `riso-mcp`. Same below-P1 note as W4-R03.

## 5. Container build scan `needs` — P0

Template: `template/files/.github/workflows/riso-container-build.yml.jinja` L183:

```jinja
needs: [{% if api_module == "enabled" and "python" in api_languages %}build-python{% endif %}{% if api_module == "enabled" and "python" in api_languages and "node" in api_languages %}, {% endif %}{% if api_module == "enabled" and "node" in api_languages %}build-node{% endif %}]
```

`scan.strategy.matrix.target` (L186–192) only emits python/node rows under the same guards. `scan` itself is **unconditional**.

Default sample (`samples/default/copier-answers.yml`): `api_module: disabled`. Copier `_exclude` (`template/copier.yml` L2057–2058) drops both container workflows when `api_module != 'enabled'`. `samples/default/render` does not exist, so dest is not present — exclude hides the default dest, it does **not** fix the jinja.

When `api_module` is enabled without python/node, the files **do** ship. Official dests (read-only):

`samples/rust-api/render/.github/workflows/riso-container-build.yml` L52–58 (`api_languages: [rust]`):

```yaml
  scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: []
    strategy:
      matrix:
        target:
```

`samples/go-api/render/.github/workflows/riso-container-build.yml` L55: `needs: []` (same empty `matrix.target`).

Contrast (valid): `samples/api-python/render/.../riso-container-build.yml` L119 `needs: [build-python]`.

GitHub Actions rejects an empty matrix (`target:` with no items). Empty `needs: []` is the condition the mission forbids.

`tests/integration/test_rendered_workflows.py` actionlint matrix is only `default`, `changelog-python`, `full-stack` — rust-api / go-api never linted.

## 6. Container publish matrix — P0

Template: `template/files/.github/workflows/riso-container-publish.yml.jinja` L27–35. `publish-ghcr` is unconditional; `matrix.target` only lists python/node.

Official dest `samples/go-api/render/.github/workflows/riso-container-publish.yml` L24–30:

```yaml
  publish-ghcr:
    name: Publish to GitHub Container Registry
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target:
    steps:
```

Same empty `target:` in `samples/rust-api/render/.github/workflows/riso-container-publish.yml` L28–30.

Contrast (valid): `samples/api-python/render/.../riso-container-publish.yml` L29–30 includes `{ name: python, dockerfile_target: runtime-python, image: api-python }`.

`go-api` dest has `go/Dockerfile` but the workflow never targets rust/go. Empty matrix is invalid even if rust/go image jobs are out of scope.

No tests render these jinja files with rust/go/disabled answers.

## Findings

| id | severity | file | issue |
| --- | --- | --- | --- |
| GATES-P0-container-build-empty-needs | P0 | `template/files/.github/workflows/riso-container-build.yml.jinja` | `scan.needs` renders `[]` and `matrix.target` is empty when api_module is disabled or languages are rust/go-only. Default dest is excluded; rust-api/go-api dests ship the broken workflow. |
| GATES-P0-container-publish-empty-matrix | P0 | `template/files/.github/workflows/riso-container-publish.yml.jinja` | `publish-ghcr` matrix `target:` is empty whenever there is no python/node API language. Live dests: rust-api + go-api. |
| GATES-CLOSED-jinja-dir-walk | closed | `scripts/ci/validate_jinja_templates.py` | Official argv `template/files` walks dirs. |
| GATES-CLOSED-ssot-gate | closed | `scripts/ci/check_removed_key_ssot.py` | 3-way key+op parity + sample leftover scan. |
| GATES-CLOSED-quality-ssot-wiring | closed | `justfile` | `just quality` / `just ci` / GHA cli-tests invoke SSOT. |
| GATES-CLOSED-skill-mirrors | closed | `.agents/skills/riso-release-readiness/` | Byte-identical to `.claude` mirror; 8-key apply-then-reject. |
| GATES-CLOSED-skill-validator | closed | `scripts/ci/validate_release_readiness_skill.py` | Mirror identity + policy contract. |
| GATES-STALE-jinja-not-a-file-docs | stale | `goals/riso-v2-release-ready/residuals/PLATFORM.md` | R3 / W4-A01-ladder still narrate `Not a file`; live script walks dirs. |

## Owner / fix (foreign trees — not this write)

Payloads / COORD (`template/files/.github/workflows/**`, optionally `template/copier.yml`):

1. Wrap `scan` so it is omitted **or** becomes a no-op that `needs: [hadolint]` when there is no python/node image job. Never emit `needs: []` or an empty `matrix.target`.
2. Wrap `publish-ghcr` the same way (omit job or valid skip) when there are no API languages that the matrix knows how to build.
3. Optional tighten: exclude container workflows unless `api_module == enabled` **and** `api_languages` intersects `{python,node}` — still fix the jinja; exclude alone left rust-api/go-api dests broken.
4. Add a render/actionlint fixture for rust-api, go-api, and api_module-disabled.

Do not hand-edit `samples/*/render/**`. Re-render via official `render-samples.sh` / `render_matrix.py` after the jinja fix.

## Path lock

| Class | Count |
| --- | --- |
| This-session writes | 1 — this evidence file |
| `samples/*/render/**` hand-edits | 0 |
| Lockfile / secret / foreign-tree edits | 0 |
| `render_matrix.py` started or killed | 0 |
