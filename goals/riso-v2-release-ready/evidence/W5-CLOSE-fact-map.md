# W5-CLOSE — accepted-fact map (live commands)

- Task: `W5-CLOSE-GOAL-EVIDENCE`
- Wave: CLOSE-GOAL-EVIDENCE
- Lane: GOAL
- Date (UTC): 2026-08-14T05:43:00Z
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- Exclusive writes: `goals/riso-v2-release-ready/**` only
- `samples/*/render/**` writes this task: **0**
- Report: `goals/riso-v2-release-ready/ASSURANCE.md`
- Source facts: `facts.md` / `facts.meta.json` (25 accepted)

**facts_covered = 24** · **facts_residual = 1** · **sum = 25**

`W4-A01-fact-map.md` is stale-doc.

| # | id | Verdict | Owner if residual | Command / proof | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | `fact-goal-kind` | green | — | no v2.0.0 tag; no commit/push/PyPI | W5-CLOSE-ladder-a.txt |
| 2 | `fact-hard-major` | green | — | existing tracks only | plan.md |
| 3 | `fact-runtime-floors` | green | — | generated python 3.11 / node 20 | mise.toml.jinja |
| 4 | `fact-tooling-canon` | green | — | `quality: lint typecheck test ssot` | justfile |
| 5 | `fact-mise` | green | — | generated mise always-on; maintainer Node 22 | W5-CLOSE-SYS-DESKTOP-MISE.md |
| 6 | `fact-openspec` | green | — | extra default disabled. Dest leftover is OPENSPEC R1 (does not flip) | copier.yml; dest default has no openspec/ |
| 7 | `fact-hypothesis-respx` | green | — | extras + shipped tests | W5-CLOSE-PY.md |
| 8 | `fact-super-migrate` | green | — | 98 remap/migrate/update; JOIN leftover 2 passed | W5-CLOSE-pytest-remap.txt |
| 9 | `fact-no-legacy-answers` | green | — | leftover rg empty; dest default answers clean; 37/37 validate | W5-CLOSE-validate.txt; dest-recheck |
| 10 | `fact-surfaces-lockstep` | green | — | 3-way SSOT 0; wizard dest lucia dropped this wave | W5-CLOSE-WEB.md |
| 11 | `fact-dirty-tree` | green | — | flatten stay-dropped; SaaS leftovers retargeted | W5-CLOSE-SAAS.md |
| 12 | `fact-wave-order` | green | — | W0→W5 evidence | evidence/ |
| 13 | `fact-write-locks` | green | — | this session GOAL-only | this file |
| 14 | `fact-correctness-first` | green | — | electron-store exclude kept | W5-CLOSE-SYS-DESKTOP-MISE.md |
| 15 | `fact-refine-stop` | **residual** | Review | no W5-R01/W5-R03; dest smoke P0s remain | residuals/GOAL.md R1 |
| 16 | `fact-just-quality` | green | — | `just quality` 0 (1067 passed / 14 skipped) | W5-CLOSE-quality.txt |
| 17 | `fact-sample-validate` | green | — | 37/37 ok:true | W5-CLOSE-validate.txt |
| 18 | `fact-jinja` | green | — | official argv 800+ OK | W5-CLOSE-ladder-a.txt |
| 19 | `fact-context-agents` | green | — | context-sync 0; `just validate-agents` 0 after official default restore | W5-CLOSE-dest-recheck.txt |
| 20 | `fact-render-matrix` | green | — | JSON present. **Not residualed.** | samples/metadata/render_matrix.json |
| 21 | `fact-docs-w` | green | — | sphinx `-W` 0 | W5-CLOSE-sphinx.txt |
| 22 | `fact-release-validators` | green | — | skill 0; workflows 11/11; official release-configs 0 | W5-CLOSE-dest-recheck.txt |
| 23 | `fact-migration-docs` | green | — | v2-migration + CHANGELOG Unreleased 2.0.0; no tag | W5-CLOSE-DOCS.md |
| 24 | `fact-no-riso-mcp` | green | — | src/riso empty; template prohibition sentences only | W5-CLOSE-ladder-a.txt |
| 25 | `fact-evidence` | green | — | this map + ASSURANCE + residuals | ASSURANCE.md |

## Counts

| class | n |
| --- | ---: |
| green | 24 |
| residual | 1 |
| blocked (`render_matrix` missing) | 0 |
| total accepted facts | 25 |
