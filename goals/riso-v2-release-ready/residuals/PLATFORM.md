# Residual — Lane PLATFORM (W5-CLOSE-GOAL-EVIDENCE)

## Summary

`samples/metadata/render_matrix.json` is present (37 variants; historical 3 `ok` / 34 `failed` from W3). **Do not residual `render_matrix.py`.** 37/37 `riso validate --json` is green. Live `just quality` is green. Official jinja argv walks dirs. Skill-mirror mismatch is closed. Official `./scripts/render-samples.sh --variant default` restored `samples/default/render` (AGENTS.md present). `just validate-agents` and official `validate_release_configs.py` are now **green**.

Remaining dest work lives in `residuals/GATES.md`, `residuals/OPENSPEC.md`, and `residuals/PY.md` (not this file’s closed rows).

`samples/*/render/**` writes this session: **0** (GOAL did not run render scripts).

## Residuals

### R1 — `just quality` (`fact-just-quality`) — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | PL-T03 / W5-CLOSE |
| **owner** | PLATFORM |
| **status** | closed |
| **command** | `just quality` |
| **blocking reason** | — |
| **redacted log** | 2026-08-14T05:36Z: ruff + ty pass; pytest **1067 passed / 14 skipped**; SSOT 3-way. `quality_exit=0`. |
| **fix** | none |
| **evidence** | `evidence/W5-CLOSE-quality.txt` |

### R2 — release-readiness skill mirror — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | PL-T07 / W1-C08-mirror |
| **owner** | PLATFORM / SKILL |
| **status** | closed |
| **command** | `uv run python scripts/ci/validate_release_readiness_skill.py` |
| **blocking reason** | — |
| **redacted log** | `skill_exit=0`. Five `REQUIRED_FILES` identical `.agents` ↔ `.claude`. |
| **fix** | none |
| **evidence** | `evidence/W5-CLOSE-ladder-a.txt`; `residuals/SKILL.md` |

### R3 — official jinja argv (`fact-jinja`) — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | PL-T04 / W5-CLOSE |
| **owner** | PLATFORM |
| **status** | closed |
| **command** | `uv run python scripts/ci/validate_jinja_templates.py template/files` |
| **blocking reason** | — |
| **redacted log** | W5-CLOSE first pass: 800 OK. Later GATES close reported 803 OK. Historical `Not a file` is stale. |
| **fix** | none |
| **evidence** | `evidence/W5-CLOSE-ladder-a.txt`; `evidence/W5-CLOSE-GATES.md` |

### R4 — default dest / `just validate-agents` (`fact-context-agents`) — **CLOSED**

| Field | Value |
| --- | --- |
| **task_id** | PL-T05 / RES-PL-04 |
| **owner** | PLATFORM |
| **status** | closed (dest restored via official `render-samples.sh`; dest **smoke** still red — `residuals/GATES.md` R2) |
| **command** | `uv run python scripts/ci/verify_context_sync.py ; just validate-agents ; uv run python scripts/ci/validate_release_configs.py` |
| **blocking reason** | — |
| **redacted log** | 2026-08-14T05:41Z dest-recheck: `samples/default/render/AGENTS.md` 217 lines; dest `.copier-answers.yml` present; dest `openspec/` absent; leftover-key `rg` empty; `just validate-agents` **exit 0** (template + 4 dest smokes 6/6); official `validate_release_configs.py` **exit 0**. |
| **fix** | none for this fact. Do not hand-edit dest. Fumadocs dest smoke is GATES/NODE. |
| **evidence** | `evidence/W5-CLOSE-dest-recheck.txt`; `evidence/W5-CLOSE-GATES.md` |
