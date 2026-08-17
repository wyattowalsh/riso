# Plan — Riso Lane COORD (v3 — parallel-team optimized)

## Executive summary

Stand up a **serial COORD contract lane** with **massively parallel** recon, verification, outbox fan-out, and payload execution around it. First `/goal` run **bootstraps process artifacts only** (under `goals/riso-lane-coord/`) and dry-runs verification; it does **not** invent `copier.yml` churn. Later runs drain a **single-writer handoff queue**.

**One-line law:** many agents may *read* contracts; only one agent may *write* COORD-owned paths; many agents may *implement payloads* only after outbox publish.

---

## 1. End-to-end critique → design responses

| Critique | Design response |
|----------|-----------------|
| COORD serial vs “massive parallel” tension | Parallelism is legal in Waves R/B/O/V/P; illegal inside Wave C file writes |
| Prior plans were step-blobs | Hyperfine graph: ~50 task IDs with owner, deps, writes, verify, agent slot |
| Handoffs unstructured | Field schemas §4 + templates as first deliverables |
| Cross-lane `generation_gates` collision | C5/O-CLI hard ban on `src/riso/**` for COORD |
| Empty inbox thrash | Idle SOP + bootstrap short-circuit |
| Verify too heavy | Staged V0–V7; matrix only on demand |
| Multi-handoff races | Change-id queue; claim lock; no multi-CID merge by default |
| Subagents need spawn recipes | §6 agent matrix with exact prompts/slots |
| Failure modes vague | §8 recovery ladder |
| Sample answers ownership | PLATFORM default; COORD only lists required key updates |

---

## 2. Architecture

### 2.1 Ownership matrix

| Path | Lane | Parallel writers allowed? |
|------|------|---------------------------|
| `template/copier.yml` | COORD | **No** (single writer) |
| `template/prompts/**` | COORD | **No** |
| `template/hooks/**` | COORD | **No** |
| `template/macros/**` | COORD | **No** |
| `template/files/module_catalog.json.jinja` | COORD | **No** |
| `.github/context/**` + `template/files/.github/context/**` | COORD | **No** (both sides one step) |
| `goals/riso-lane-coord/**` | COORD | Yes if **file-disjoint** |
| `src/riso/**` | CLI | Not COORD |
| `template/files/python/**` | PY | After outbox |
| `template/files/node/**` ¬saas | NODE | After outbox |
| `template/files/node/saas/**` | SAAS | After outbox |
| `template/files/go/**`, `rust/**` | SYS | After outbox |
| `template/files/electron/**`, `tauri/**` | DESKTOP | After outbox |
| `template/files/frontend/**` | FE | After outbox |
| `template/files/quality/**`, `testing/**` | QUAL | After outbox |
| `samples/*/copier-answers.yml` | PLATFORM | After outbox (preferred) |
| `samples/*/render/**` | nobody hand-edits | regenerate only |

### 2.2 Live inventory (repo-grounded)

- `copier.yml` ~2133 LOC; large defaults + questions surface  
- Hooks: `pre_gen` ~794, `post_gen` ~598; import `validate_answers_for_generation`  
- Catalog modules: quality, cli, api_python, api_node, graphql_api, mcp_module, websocket_module, docs_framework, shared_logic, workflow_generation, changelog_release  
- Macros: `module_flags.jinja`, `agent_commands.jinja`, `ci_paths.jinja`  
- Context: 9 mirrored files; **parity currently green**  
- Samples: ~23 `copier-answers.yml` variants  
- CLI: `riso validate|prompts|catalog`  
- Tests: large hook suites + `test_verify_context_sync.py`

### 2.3 Wave topology

```text
        ┌──────────────────────────────────────────┐
        │ Wave R  READ-ONLY RECON (N agents)       │
        └──────────────────┬───────────────────────┘
                           ▼
        ┌──────────────────────────────────────────┐
        │ Wave B  BOOTSTRAP docs (file-disjoint N) │  ← first empty-inbox run only
        └──────────────────┬───────────────────────┘
                           ▼
        ┌──────────────────────────────────────────┐
        │ Wave C  COORD APPLY (1 writer, 1 CID)    │  ← serial heart
        └──────────────────┬───────────────────────┘
                           ▼
        ┌──────────────────────────────────────────┐
        │ Wave O  OUTBOX FAN-OUT (N messengers)    │
        └──────────────────┬───────────────────────┘
                           ▼
        ┌──────────────────────────────────────────┐
        │ Wave P  PAYLOAD (N exclusive lanes)      │  ← other goals; COORD stops
        └──────────────────┬───────────────────────┘
                           ▼
        ┌──────────────────────────────────────────┐
        │ Wave V  VERIFY (parallel cmds → 1 audit) │
        └──────────────────────────────────────────┘
```

V can also run **after B** (bootstrap dry-run) without C/O/P.

---

## 3. Hyperfine task graph

### Notation

`ID | title | owner | par? | deps | writes | verify | agent_slot`

`par? = Y` means parallel with same-wave peers **iff write sets disjoint**.

### Wave R — Recon (all read-only; max parallel)

| ID | Title | Owner | Par | Deps | Writes | Verify | Slot |
|----|-------|-------|-----|------|--------|--------|------|
| R0 | Enforce no git branch/commit/push unless human asked | lead | Y | — | ∅ | policy noted | lead |
| R1 | List `goals/riso-lane-coord/inbox/*` | recon | Y | — | ∅ | file list | R-a |
| R2 | List `goals/riso-lane-*/handoffs/*` | recon | Y | — | ∅ | file list | R-b |
| R3 | Parse each handoff → surface matrix (copier/hooks/macros/catalog/context/gates) | recon | Y | R1,R2 | ∅ | matrix rows | R-c |
| R4 | Read `generation_gates.py` + `removed_answer_keys.py` vs proposed keys | recon | Y | R3 | ∅ | CLI-needed flag | R-d |
| R5 | Map existing tests covering touched rules | recon | Y | R3 | ∅ | test ids | R-e |
| R6 | Map affected `samples/*/copier-answers.yml` | recon | Y | R3 | ∅ | sample paths | R-f |
| R7 | Baseline context parity | recon | Y | — | ∅ | `verify_context_sync` 0 | R-g |
| R8 | Build ordered CID queue + reject incomplete handoffs plan | lead | N | R3–R7 | ∅ | queue doc | lead |
| R9 | Path-lock plan: which exact files Wave C will touch | lead | N | R8 | ∅ | lock list | lead |

**Empty-inbox branch:** R1∪R2 empty → if first run: Wave B; else idle SOP (no C).

**Spawn recipe (parallel):** slots R-a…R-g as explore/read-only agents with disjoint read foci; lead synthesizes R8–R9.

### Wave B — Bootstrap (first run; file-disjoint writers)

| ID | Title | Owner | Par | Deps | Writes | Verify | Slot |
|----|-------|-------|-----|------|--------|--------|------|
| B1 | `inbox/` + `.gitkeep` | fs | Y | R0 | `.../inbox/` | exists | B-a |
| B2 | `outbox/` + `.gitkeep` | fs | Y | R0 | `.../outbox/` | exists | B-b |
| B3 | `handoff-template.md` (§4.1 full) | docs | Y | R0 | handoff-template | headings | B-c |
| B4 | `outbox-template.md` (§4.2 full) | docs | Y | R0 | outbox-template | headings | B-d |
| B5 | `LANE.md` ownership+waves+idle+secrets+uv | docs | Y | R0 | LANE.md | facts coverage | B-e |
| B6 | `APPLY-CHECKLIST.md` serial micro-steps C0–C10 | docs | N | B5 | APPLY-CHECKLIST | usable alone | B-f |
| B7 | `README.md` index | docs | N | B1–B6 | README.md | links | B-g |
| B8 | `outbox/bootstrap-verify.md` evidence skeleton | docs | Y | B2 | bootstrap-verify | exists | B-h |
| B9 | `examples/minimal-handoff.md` worked example (fictional key) | docs | Y | B3 | examples/ | clearly marked example | B-i |
| B10 | `examples/minimal-outbox.md` worked example delta | docs | Y | B4 | examples/ | marked example | B-j |

**Parallel panels:**  
- Panel B1: B1∥B2∥B3∥B4∥B5∥B8∥B9∥B10  
- Panel B2: B6 → B7  

### Wave C — Apply one CID (serial single writer)

| ID | Title | Deps | Writes | Verify |
|----|-------|------|--------|--------|
| C0 | Claim CID (status=in_progress) | R9 | inbox/CID.md | sole claim |
| C1 | Schema-complete check vs §4.1; else reject outbox | C0 | maybe outbox reject | pass/fail |
| C2a | Edit `template/copier.yml` keys/when/default/help | C1 | copier.yml | keys exist |
| C2b | Edit `template/prompts/**` if needed | C2a | prompts | coherent |
| C3 | Edit `template/macros/**` | C2a | macros | syntax |
| C4a | Edit `pre_gen_project.py` validation | C2a | pre_gen | rule present |
| C4b | Edit `post_gen_project.py` if metadata/guidance | C2a | post_gen | rule present |
| C4c | Edit `validators/**` if split helpers | C4a | validators | import ok |
| C5 | Draft CLI gates ticket text (no `src/riso` edit) | C4a | goals only | ticket text |
| C6 | Edit `module_catalog.json.jinja` | C2a,C3 | catalog | renders |
| C7a | Write `.github/context/*` | C1 | context src | files |
| C7b | Mirror to `template/files/.github/context/*` | C7a | context mirror | digests equal |
| C8 | Forbidden-path audit (`git status` allowlist) | C2–C7 | ∅ | clean |
| C9 | Write `outbox/CID.md` | C8,C5 | outbox | complete |
| C10 | Archive/mark applied | C9 | inbox | status |

**Strict serial edges:** never C2a∥C2b across two agents; never C4a∥C6 if both need same answer key semantics without one brain. Preferred: **one COORD agent** executes C0–C10.

**Optional micro-parallel only inside one agent’s tool calls:** e.g. read files in parallel before write.

### Wave O — Fan-out (parallel messengers; disjoint targets)

| ID | Title | Par | Deps | Writes |
|----|-------|-----|------|--------|
| O0 | Ensure `outbox/CID.md` is SSOT | N | C9 | outbox |
| O-CLI | CLI gates section/ticket | Y | O0 | cli inbox optional |
| O-PY | PY payload section | Y | O0 | optional copy |
| O-NODE | NODE section | Y | O0 | optional |
| O-SAAS | SAAS section | Y | O0 | optional |
| O-SYS | SYS section | Y | O0 | optional |
| O-DESK | DESKTOP section | Y | O0 | optional |
| O-FE | FE section | Y | O0 | optional |
| O-QUAL | QUAL section | Y | O0 | optional |
| O-PLAT | PLATFORM answers/CI section | Y | O0 | optional |

**Default:** single SSOT outbox with sections (O0 only). Copies O-* only if sibling lane packages exist and want local inbox files.

### Wave P — Payload (other lanes; listed for orchestration)

| ID | Lane | Deps | Writes |
|----|------|------|--------|
| P-PY…P-PLAT | exclusive | matching O-* + C9 | exclusive roots |

COORD **does not** run P.

### Wave V — Verification (parallel commands)

| ID | Title | When | Par | Command |
|----|-------|------|-----|---------|
| V0 | CLI present | always | — | `uv run riso --help` |
| V1 | Context sync | context\|\|bootstrap | Y | `uv run python scripts/ci/verify_context_sync.py` |
| V2.i | Validate sample *i* | apply\|\|bootstrap | Y per i | `uv run riso validate --answers-file samples/<i>/copier-answers.yml --json` |
| V3p | Prompts smoke | prompts\|\|bootstrap | Y | `uv run riso prompts --json` |
| V3c | Catalog smoke | catalog\|\|bootstrap | Y | `uv run riso --json catalog modules` |
| V4 | Hook tests (narrow `-k`) | hooks changed | Y | `uv run pytest tests/unit/hooks/... -q -n 0` |
| V5 | Context unit tests | context changed | Y | `uv run pytest tests/unit/ci/test_verify_context_sync.py -q -n 0` |
| V6 | Path allowlist audit | always after writes | N | `git status` parse |
| V7 | Full render matrix | human / unprovable only | N | render scripts — **not default** |
| V8 | Write evidence block into outbox/bootstrap-verify | end | N | markdown append |

**Bootstrap panel:** `V0 → (V1 ∥ V3p ∥ V3c) → V2.default → (optional V4 smoke) → V6 → V8`

**Post-apply panel:** `V0 → V6 → (V1? ∥ V5?) → (V4?) → (V3p? ∥ V3c?) → parallel V2.i → patch C9 evidence`

---

## 4. Schemas

### 4.1 Inbound handoff (required fields)

```yaml
change_id: string
requesting_lane: enum
summary: string
status: proposed|in_progress|applied|rejected
needs_shared_generation_gates: bool
prompt_keys: [{key, type, default, when, help, choices?}]
illegal_combinations: [{condition, error_message, preferred_surface: hooks_local|gates_shared}]
module_catalog: [{name, prompt_key, default_state, selected_state, dependencies, docs_path, ci_jobs, validation_commands}]
macros: [{file, change}]
context_snippets: [{filename, intent}]
payload_followups: [{lane, paths[], acceptance}]
samples_to_validate: [path]
non_goals: [string]
```

Markdown template renders these as sections/tables (interview chose markdown, not JSON).

### 4.2 Outbound contract delta (required fields)

```yaml
change_id: string
applied_at: iso8601
status: applied|rejected|partial
answer_keys_changed: [{key, before, after}]
illegal_combos_enforced: [{rule, location}]
module_catalog_rows: [{name, change}]
context_files: [{file, action, parity_verified}]
cli_handoff_required: {yes: bool, summary: string}
payload_checklist: [{lane, paths[], done: bool}]
verification_evidence: [{stage, command, result}]
residual_risks: [string]
coord_paths_closed: true  # payload must not re-edit COORD
```

---

## 5. Decision trees

### 5.1 Gates vs hooks

```text
Rule must hold in `riso validate` / copy generation?
  yes → CLI handoff (generation_gates / REMOVED_ANSWER_KEYS); COORD does not edit src/riso
  no  → hook-local UX/tooling OK (install hints, soft checks)
Both need user-visible pre_gen errors and shared validate?
  → implement shared gate via CLI outbox first when possible; temporary hook-only only if blocked
```

### 5.2 Empty inbox

```text
no handoffs?
  bootstrap artifacts missing? → Wave B + V dry-run → done
  else → idle: report queue empty; do not invent keys
```

### 5.3 Smallest coherent set

```text
new answer key?
  → copier (+prompts) + catalog selected_state + illegal combo rules + macros if referenced
context doc only?
  → C7a+C7b only + V1
catalog row only (expression fix)?
  → C6 + V3c (+ samples if validate breaks)
```

### 5.4 Multi-CID

```text
default: strict queue one CID
human requests batch? → still serial C waves; may pipeline O/V of CID_n with C of CID_n+1
  ONLY if write sets proven disjoint (rare for copier.yml)
```

---

## 6. Subagent spawn matrix (massive parallel)

### 6.1 Bootstrap run (recommended slots)

| Slot | Type | Tasks | Capability |
|------|------|-------|------------|
| lead | parent | R0,R8,R9, synthesize, V6,V8 | all |
| R-a…R-g | explore read-only | R1–R7 | read-only |
| B-a…B-e,B-h…B-j | general-purpose | B1–B5,B8–B10 | read-write, **file-locked** |
| B-f,B-g | sequential after B5 | B6,B7 | read-write |
| V-ctx | execute | V1 | execute |
| V-prompts | execute | V3p | execute |
| V-catalog | execute | V3c | execute |
| V-validate | execute | V2.default | execute |

**Conflict check:** B writers only touch distinct paths under `goals/riso-lane-coord/`.

### 6.2 Apply run slots

| Slot | Tasks | Notes |
|------|-------|-------|
| lead-COORD | full C0–C10 | **only writer** on template contracts |
| recon swarm | R* | parallel before claim |
| V swarm | V* | after C8/C9 |
| messengers | O-* | optional; prefer SSOT outbox |

### 6.3 Anti-patterns (do not spawn)

- Two agents editing `copier.yml`  
- Payload agent “helping” with hooks  
- COORD agent implementing `template/files/python/**`  
- Verify agent auto-fixing by editing contracts without claim  
- Full matrix agent by default  

---

## 7. First `/goal` concrete sequence

```text
R0
R1∥R2∥R7          # expect empty inbox on first setup
→ Wave B panel1: B1∥B2∥B3∥B4∥B5∥B8∥B9∥B10
→ B6 → B7
→ V0
→ V1∥V3p∥V3c
→ V2.default
→ optional V4 smoke (pre_gen import only / -k removed_keys)
→ V6 path audit (only goals/riso-lane-coord/**)
→ V8 evidence
→ DONE
```

**Success evidence:** files exist; context sync green; default validate green; prompts/catalog JSON envelopes ok; no template contract diffs from this run.

---

## 8. Recovery ladder

| Failure | Action |
|---------|--------|
| Incomplete handoff | C1 reject outbox; do not partial-apply |
| Context parity fail | fix C7a/C7b only; re-V1; never “fix” by deleting context |
| `riso validate` fail on old samples | if new required keys: O-PLAT; if illegal combo bug: fix C4/C5 path |
| Hook test fail | narrow fix C4*; re-V4; no payload edits |
| Accidentally touched forbidden path | revert that path immediately; V6 |
| CLI gates urgently needed | stop COORD apply at contract; O-CLI; do not fork logic long-term |
| Agent crash mid-C | status stays in_progress; resume same CID; no second claimer |
| Human says expand to matrix | only then V7 |

---

## 9. Fact → task coverage

| Fact | Tasks |
|------|-------|
| protocol only | B*, empty-inbox idle |
| exclusive / forbidden writes | ownership matrix, C8, V6 |
| no git unless asked | R0 |
| handoff md + template | B3, §4.1, B9 |
| outbox delta + template | B4, C9, §4.2, B10 |
| smallest coherent / clean state | §5.3, APPLY-CHECKLIST |
| illegal combos | C4*, V4 |
| gates → CLI | C5, O-CLI |
| context parity | C7*, V1, V5 |
| module_catalog | C6, V3c |
| payload stop | no Wave P for COORD |
| verify default | Wave V stages |
| bootstrap first run | §7 |
| uv run | all commands |
| no secrets | LANE.md |
| no render hand-edit | ownership + V6 |

---

## 10. Risks

1. **Serial bottleneck is the product** of multi-agent safety — optimize around it, not through it.  
2. **Hook/CLI dual validation** until O-CLI lands.  
3. **Large hook tests** — always prefer `-k` slices.  
4. **23 samples** — validate affected set only; default on bootstrap.  
5. **Sibling goals empty** — SSOT outbox must stand alone.  
6. **Example handoffs** must be marked non-executable so agents don’t apply fiction.  
7. **PLATFORM answers** may lag new defaults; list explicitly in outbox.  

---

## 11. Done checklist

### Bootstrap

- [ ] Templates + LANE + APPLY-CHECKLIST + README + examples + inbox/outbox  
- [ ] V1, V2.default, V3p, V3c green  
- [ ] V6: no unsolicited `template/**` contract edits  
- [ ] Evidence in `outbox/bootstrap-verify.md`  
- [ ] No branch/commit/push unless asked  

### Apply (later)

- [ ] One CID C0–C10 complete  
- [ ] Outbox SSOT with payload + CLI sections  
- [ ] Staged V* green for touched surfaces  
- [ ] Payload lanes unblocked without COORD re-entry  

---

## 12. Non-goals (this package)

- Implementing FastAPI/Node/SaaS/desktop/Go/Rust bodies  
- Editing `src/riso` generation_gates  
- Full sample matrix regen by default  
- Creating git branches/PRs unless human asks  
- Inventing product prompt keys without a handoff  
