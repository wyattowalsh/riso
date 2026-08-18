# W5-R2 — Review pass 2, surface=CLI

- Date: 2026-08-18
- Mode: independent re-read of live files (pass 1 untrusted)
- Status: **no new P0 / no new P1**

## Pass 1 disposition

| id                      | Verdict                                                                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CLI-P1-export-list-data | **fixed** — `format_data_assignment` YAML-dumps lists; `_coerce_value` YAML-parses; `test_export_cli_wrap_list_round_trips_through_parse_and_validate` |

## P0

None.

## P1

None.

Apply-then-reject remains wired at resolve/validate/copy/export/migrate/update/recopy/diff/generation_gates. Lucia fail-closed. No `riso-mcp` under `src/riso`.
