# W5-R2 — Review pass 2, surface=gates

- Date: 2026-08-18
- Mode: independent re-read of live files + live ladder commands
- Status: **no new P0 / no new P1**

## Pass 1 disposition

| id                             | Verdict                                                                   |
| ------------------------------ | ------------------------------------------------------------------------- |
| GATES-P0-sphinx-make-linkcheck | **fixed in source** — `sphinx_linkcheck_command` prefers `just linkcheck` |
| GATES-P1-mise-trust            | **fixed in source** — `mise trust` dest pin after official copy           |

## Live ladder (this pass)

| Command                               | Result                                  |
| ------------------------------------- | --------------------------------------- |
| jinja `template/files`                | 803 OK                                  |
| `check_removed_key_ssot.py`           | 3-way parity; zero leftover sample keys |
| `verify_context_sync.py`              | 0                                       |
| `validate_release_readiness_skill.py` | 0                                       |
| `validate_workflows.py`               | 11/11                                   |
| `validate_release_configs.py`         | 0                                       |
| 37 × `riso validate --json`           | 37/37 ok                                |
| leftover-key `rg`                     | empty                                   |
| `rg riso-mcp src/riso template`       | prohibition sentences only              |
| `sphinx-build -W`                     | 0                                       |
| `git tag -l v2.0.0 2.0.0`             | empty                                   |

## New this pass (not a review P0)

Official `render-samples.sh` failed pre_gen with "No Copier answers" because Copier tasks do not export `COPIER_ANSWERS` and do not chdir to dest. Fixed in this closeout: export JSON from `--answers` and chdir/`COPIER_ANSWERS` from dest `.copier-answers.yml` in `_tasks`. Re-render required for `just validate-agents` / dest-dependent pytest.
