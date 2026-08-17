# W5-CLOSE — official ladder rollup

- Date (UTC): 2026-08-14T05:43:00Z
- Cwd: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b`
- `render_matrix.py` live process: **none** (not started; not killed)
- Python: `uv run` only

| Command | Exit | Log |
| --- | ---: | --- |
| `just quality` | **0** | `W5-CLOSE-quality.txt` — **1067 passed / 14 skipped** |
| 37 × `riso validate --json` | **0** | `W5-CLOSE-validate.txt` `TOTAL=37 OK=37 FAIL=0` |
| `validate_jinja_templates.py template/files` | **0** | `W5-CLOSE-ladder-a.txt` — 800 OK (later GATES: 803) |
| `verify_context_sync.py` | **0** | `W5-CLOSE-ladder-a.txt` |
| `just validate-agents` (before dest restore) | 1 | `W5-CLOSE-validate-agents.txt` — stale |
| `just validate-agents` (after official default restore) | **0** | `W5-CLOSE-dest-recheck.txt` |
| `check_removed_key_ssot.py` | **0** | ladder-a + quality |
| `render_matrix.py` | not re-run | JSON present (37 variants) |
| `sphinx-build -W` | **0** | `W5-CLOSE-sphinx.txt` |
| `validate_release_readiness_skill.py` | **0** | |
| `validate_workflows.py` | **0** | 11/11 |
| `validate_release_configs.py` (before dest) | 1 | dest absent — stale |
| `validate_release_configs.py` (after dest) | **0** | dest-recheck |
| leftover-key `rg` sample + dest answers | empty | dest-recheck |
| `rg riso-mcp src/riso template` | 0 in src; 2 prohibition hits | |
| remap/migrate/update pytest | **0** (98) | `W5-CLOSE-pytest-remap.txt` |
| JOIN leftover pytest | **0** (2) | same |
| `git tag -l 'v2.0.0' '2.0.0'` | empty | |

Default dest restored by official `./scripts/render-samples.sh --variant default` (GATES; not this session). Dest smoke still fails Fumadocs `/sitemap.xml` + `output: export` (`samples/default/smoke-results.json` 2026-08-14T05:39:27Z).
