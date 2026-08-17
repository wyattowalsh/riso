# Plan — Riso Lane CLI

**Status:** execution-ready for parallel subagent teams.
**Companion:** [`tasks.graph.json`](./tasks.graph.json) · [`facts.md`](./facts.md)

---

## 1. Mission

Own maintainer **`riso` CLI** (`src/riso/**`) + **`tests/unit/test_cli/**`**. Keep agent-native contracts reliable (JSON envelope, exit codes, paths, timeouts). Expand missing unit coverage. Improve commands only inside owned paths. Never reintroduce `riso-mcp`. Never write template contracts (COORD handoff).

| Priority (interview: all) | Staging |
|---------------------------|---------|
| Reliability | only if red or tasked |
| Coverage | **default next value** (P0 gaps) |
| New/expanded commands | when tasked |

---

## 2. Live evidence (2026-07-25)

| Probe | Result |
|-------|--------|
| `uv run riso --help` | **0** |
| `uv run riso doctor --json` | **ok=true ready=true** envelope keys complete |
| `uv run pytest tests/unit/test_cli/ -q` | **54 passed** |
| `uv run riso --json catalog modules\|dependencies` | **ok** |
| `uv run riso --json variants list` | **ok** |
| `uv run riso --json prompts` | **ok** |
| mcp under `src/riso` | **none** |

**Kill switch:** If Recipe A re-probes stay green, **skip W1–W3**. Jump to **W4 P0** only when coverage is in scope; otherwise DONE after W6.

---

## 3. End-to-end critique

| # | Finding | Severity | Plan control |
|---|---------|----------|--------------|
| 1 | Baseline already green — rework is waste | High | Recipe A short-circuit |
| 2 | `prompts.py` / `variants.py` / `recopy.py` have **zero dedicated tests** despite live OK | **P0** | C4.01–03 parallel new files |
| 3 | Shared `answers.py` is a fan-out chokepoint | Med | S-ANS serial pre-W2 |
| 4 | `app.py` `_normalize_argv` untested | Med | C4.06 alone on S-APP |
| 5 | Parallel theme agents thrash `output.py` | High | exclusive shards |
| 6 | Template edits “fix” CLI | Critical | denylist + H5 handoffs |
| 7 | `just quality` always-on | Med | V6.07 optional only |
| 8 | Error JSON goes to **stderr** (`emit_error`) | Low | tests must capture stderr |

---

## 4. Boundaries

**Write:** `src/riso/**`, `tests/unit/test_cli/**`, optional `goals/riso-lane-cli/handoffs/**`
**Never write:** template files/hooks/copier.yml/macros/module_catalog, web/, samples render/answers, scripts/ci, lockfile hand-edits, secrets, unsolicited git branch/commit/push, riso-mcp
**Always:** `uv run`
**Out of scope:** PY generated CLI, COORD contracts, PLATFORM CI, web

---

## 5. Shard lock table

| Shard | Write paths | Conflicts with |
|-------|-------------|----------------|
| S-OUT | `cli/output.py`, `test_output.py` | all emit consumers until freeze |
| S-APP | `cli/app.py`, `test_argv_normalize.py` | any wiring change |
| S-CFG | `config.py`, `helpers.py`, `test_helpers.py` | commands using helpers |
| S-ERR | `core/errors.py` | all |
| S-PATH | `paths.py`, `names.py`, `test_paths.py` | dest/template users |
| S-ANS | answers/gates/removed_keys + tests | validate/export/copy |
| S-DIFF | `core/diff.py`, `test_diff_ignore.py` | dry-run paths |
| S-TPL | worker, hooks, timeout + control-plane tests | mutation cmds |
| S-DOC | `doctor.py`, `test_doctor.py` | — |
| S-VAL | `validate.py`, `test_validate.py` | S-ANS |
| S-COPY | `copy.py` | S-TPL, S-ANS |
| S-UPD | `update.py` | S-TPL |
| S-RCP | `recopy.py`, `test_recopy.py` | S-TPL |
| S-DFC | `commands/diff.py` | S-DIFF optional |
| S-VAR | `variants.py`, `test_variants.py` | — |
| S-CAT | `catalog.py`, `test_catalog.py` | — |
| S-PRM | `prompts.py`, `test_prompts.py` | — |
| S-EXP | `export.py`, `test_export.py` | S-ANS |
| S-HND | handoffs | — |
| S-VFY | ∅ | — |

**One writer per shard. New test files maximize ∥.**

---

## 6. Critical path

```
Recipe A (default):
  C0.01∥C0.02∥C0.03∥C0.09 → V6.01–03 → V6.08 → DONE  (~minutes)

Recipe C (max value now):
  C4.01∥C4.02∥C4.03 → V6.03 → V6.08 → DONE
  critical path length = 1 wave (3 independent files)

Recipe D:
  [optional S-ANS] → 6-way W2 → W2-gate → W6

Recipe E:
  S-TPL freeze → 4-way W3 → W3-gate → W6
```

**Longest serial chain if everything broken:**
C1.01→C1.03→C1.04→C1.05→W3→W6 (foundation then mutation). Avoid unless red.

---

## 7. File×agent safety matrix (merge conflicts)

| File | Max concurrent writers | Notes |
|------|------------------------|-------|
| `test_prompts.py` (new) | 1 | C4.01 only |
| `test_variants.py` (new) | 1 | C4.02 only |
| `test_recopy.py` (new) | 1 | C4.03 only |
| `test_output.py` | 1 | C4.07+C4.12 same agent |
| `app.py` | 1 | never parallel |
| `answers.py` | 1 | before validate/export |
| `doctor.py` | 1 | — |
| disjoint command modules | N | W2/W3 fan-out |

---

## 8. Hyperfine task cards

### W0 — Baseline (R/X · ∥12)

| ID | Kind | Cmd / action | Pass |
|----|------|--------------|------|
| C0.01 | X | `uv run riso --help` | exit 0 |
| C0.02 | X | `uv run riso doctor --json` | ok, keys |
| C0.03 | X | `uv run pytest tests/unit/test_cli/ -q` | 54+ pass |
| C0.04 | R | map cmd→run_*→test | matrix |
| C0.05 | R | emit audit | list |
| C0.06 | R | ExitCode audit | matrix |
| C0.07 | R | timeout graph | graph |
| C0.08 | R | argv edges | cases |
| C0.09 | R | no mcp | clean |
| C0.10 | R | gap rank | P0 list |
| C0.11 | X | introspect --json | ok |
| C0.12 | R | owned vs handoff | plan |
| C0.13 | W | handoff note optional | file |

**t0:** 01–09 ∥ · **t1:** 10∥11 · **t2:** 12→13

### W1 — Foundation (only if red)

| ID | Shard | Dep | Work |
|----|-------|-----|------|
| C1.01 | S-ERR | C0.06 | errors consistency |
| C1.02 | S-PATH | C1.01 | paths + tests |
| C1.03 | S-OUT | C1.01 | envelope + tests |
| C1.04 | S-CFG | C1.02,C1.03 | config/helpers |
| C1.05 | S-TPL | C1.04 | worker API freeze |
| C1.06 | S-HND | C1.05 | freeze note |

Order: `01 → (02∥03) → 04 → 05 → 06`

### W2 — RO fan-out (∥6)

| Agent | IDs | Shard | Leaf acceptance |
|-------|-----|-------|-----------------|
| A1 | C2.D1,D2 | S-DOC | doctor edge cases unit + `doctor --json` |
| A2 | C2.V1,V2 | S-VAL | validate requires inputs; removed keys |
| A3 | C2.C1,C2 | S-CAT | modules+dependencies data keys |
| A4 | C2.P1,P2 | S-PRM | list keys; unknown show fails |
| A5 | C2.R1,R2 | S-VAR | list count; unknown show fails |
| A6 | C2.E1,E2 | S-EXP | quoting; yaml single envelope |

Pre: C2.V0/G1/K1 on S-ANS if answers change.

### W3 — Mutation fan-out (∥4 post S-TPL)

| Agent | IDs | Shard | Leaf acceptance |
|-------|-----|-------|-----------------|
| M1 | C3.C1,C2 | S-COPY | dry_run/force/jail mocked |
| M2 | C3.U1,U2 | S-UPD | corrupt answers / gates |
| M3 | C3.R1,R2 | S-RCP | missing dest; skip_post_gen |
| M4 | C3.D1∥D2 | S-DFC∥S-DIFF | operation flag; ignore rules |

### W4 — Coverage (default value wave)

#### P0 leaf cards (run first · full parallel)

**C4.01 · S-PRM · `tests/unit/test_cli/test_prompts.py` (new)**

```text
GIVEN template path resolves
WHEN run_prompts_list(config)
THEN data has prompts:dict, defaults:dict
WHEN run_prompts_show(config, "__no_such_key__")
THEN ValidationFailedError
Verify: uv run pytest tests/unit/test_cli/test_prompts.py -q
```

**C4.02 · S-VAR · `tests/unit/test_cli/test_variants.py` (new)**

```text
WHEN run_variants_list(config)
THEN variants:list, count==len(variants)
WHEN run_variants_show(config, "__no_such__")
THEN PathNotFoundError
Verify: uv run pytest tests/unit/test_cli/test_variants.py -q
```

**C4.03 · S-RCP · `tests/unit/test_cli/test_recopy.py` (new)**

```text
WHEN run_recopy(..., destination=missing)
THEN PathNotFoundError
WHEN dry_run with tmp project fixture (mock compute_diff if needed)
THEN dict payload without writing template
Verify: uv run pytest tests/unit/test_cli/test_recopy.py -q
```

#### P1–P2 (second wave)

| ID | Shard | File | Assert |
|----|-------|------|--------|
| C4.04 | S-VAL | test_validate.py | no -f/-d → ValueError/usage |
| C4.05 | S-DOC | test_doctor.py | not ready if template missing |
| C4.06 | S-APP | test_argv_normalize.py | `--json` after subcmd reordered |
| C4.07 | S-OUT | test_output.py | emit_error stderr JSON ok=false |
| C4.08 | S-CAT | test_catalog.py | lock exists flags |
| C4.09 | S-DFC | tests | bad operation |
| C4.10 | S-TPL | timeout tests | SIGTERM→KILL |
| C4.11 | S-EXP | test_export.py | alias command name |
| C4.12 | S-OUT | test_output.py | quiet (same agent as C4.07) |

### W5 — Handoffs

| ID | Trigger | Path |
|----|---------|------|
| H5.01 | prompt contract | handoffs/coord-prompts.md |
| H5.02 | hooks | handoffs/coord-hooks.md |
| H5.03 | catalog schema | handoffs/coord-catalog.md |
| H5.04 | sample answers | handoffs/platform-samples.md |
| H5.05 | CI CLI | handoffs/platform-ci.md |

### W6 — Verify

| ID | Command | Required |
|----|---------|----------|
| V6.01 | `uv run riso --help` | yes |
| V6.02 | `uv run riso doctor --json` | yes |
| V6.03 | `uv run pytest tests/unit/test_cli/ -q` | yes |
| V6.04 | `uv run riso --json catalog modules` | if touched |
| V6.05 | `uv run riso --json prompts` | if touched |
| V6.06 | `uv run riso --json variants list` | if touched |
| V6.07 | `just quality` | rare |
| V6.08 | `git status` allowlist | yes |

---

## 9. Recipes (dispatch)

### A — Health (default `/goal`)

```
parallel explore/execute: C0.01 C0.02 C0.03 C0.09
serial: V6.01 V6.02 V6.03 V6.08
STOP if green
```

### B — Single bug/feature

```
shard claim → edit + tests → pytest path -q → W6
```

### C — Coverage P0 ★ recommended next

```
parallel writers: C4.01 C4.02 C4.03
serial: V6.03 V6.08
```

### D — RO day

```
6 agents W2 → W2 gate → W6
```

### E — Mutation day

```
S-TPL freeze → 4 agents W3 → W3 gate → W6
```

### Recovery ladder

1. pytest fail in one shard → fix same shard only
2. cross-shard API break → roll back to freeze note; serialize
3. forbidden path temptation → H5 handoff; stop
4. flaky timeout → mock; do not loosen production kill

---

## 10. Spawn templates

### Explore (W0)

```
READ-ONLY riso CLI lane. Task <ID>. No edits.
Return: pass/fail, file:line, P0 gaps only.
```

### Writer (W2–W4)

```
WRITE ONLY your shard paths. Task <ID>.
uv run only. No template/hooks/web/samples answers/ci/locks/secrets/git push.
Envelope stable. Tests match behavior.
Verify: <pytest file> then report files+cmds+risks.
```

### LEAD

```
Orchestrate recipes. Never parallel same file.
Enforce denylist via git status (V6.08).
Prefer Recipe A then C for value.
```

---

## 11. Done

- [ ] Recipe A green (or reds fixed in-lane / handed off)
- [ ] If coverage tasked: C4.01–03 landed + V6.03
- [ ] Behavior diffs include tests
- [ ] No forbidden writes; no riso-mcp; COORD gaps handed off

---

## 12. Commands

```bash
uv run riso --help
uv run riso doctor --json
uv run pytest tests/unit/test_cli/ -q
uv run riso --json catalog modules
uv run riso --json prompts
uv run riso --json variants list
```
