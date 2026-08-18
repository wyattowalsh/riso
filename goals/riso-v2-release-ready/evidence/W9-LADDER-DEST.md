# W9 — official default dest + dest-gated ladder

| Command                                                                                      | Exit       | Notes                                                              |
| -------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------------------------------ |
| `./scripts/render-samples.sh --variant default --answers samples/default/copier-answers.yml` | **0**      | dest `AGENTS.md`; no leftover `openspec/`; docs smoke passed 19.4s |
| `just validate-agents`                                                                       | **0**      | default + cli-docs + full-stack + ai-tools-off                     |
| `check_removed_key_ssot.py`                                                                  | **0**      | 3-way parity; leftover sample keys empty                           |
| `validate_jinja_templates.py` (W9 shims)                                                     | **0**      | health / env / observability logger                                |
| `git tag -l v2.0.0 2.0.0`                                                                    | empty      |                                                                    |
| `render_matrix.py`                                                                           | not re-run | JSON present; 37 variants; 30 ok / 7 dest-smoke red                |

No dest hand-edits. No second matrix start/kill.
