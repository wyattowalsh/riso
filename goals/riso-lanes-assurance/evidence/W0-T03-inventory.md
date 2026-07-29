# W0-T03 evidence — dirty inventory

- Captured (UTC): `2026-07-29T01:21:58Z`
- Repo: `/Users/ww/dev/projects/riso` branch `main` HEAD `9b62b31`
- Task: W0-T03 map every dirty path → exactly one lane
- Artifact: `goals/riso-lanes-assurance/inventory-dirty.md`

## Commands

```bash
git rev-parse --show-toplevel
git status --short
git diff --name-only
git ls-files --others --exclude-standard
```

## Result summary

| Metric                     | Value |
| -------------------------- | ----: |
| Total dirty leaf paths     |   222 |
| Tracked (diff --name-only) |    54 |
| Untracked                  |   168 |
| COORD                      |    19 |
| PY                         |    26 |
| NODE                       |     8 |
| SAAS                       |     8 |
| SYS                        |    41 |
| DESKTOP                    |     9 |
| CLI                        |    18 |
| PLATFORM                   |    67 |
| ASSURANCE                  |    24 |
| OUT-OF-SCOPE               |     2 |

## Completeness

- Every dirty path assigned exactly one of: COORD|PY|NODE|SAAS|SYS|DESKTOP|CLI|PLATFORM|ASSURANCE|OUT-OF-SCOPE
- Unowned: 0
- Status: **green**

## OUT-OF-SCOPE (owned as OOS, not residual blockers)

- `??` `.claude/skills/mcp-installer/uv.lock` — local harness/tooling outside exclusive lane roots
- `??` `.grok/workflows/riso-lanes-assurance.rhai` — local harness/tooling outside exclusive lane roots

## Lane package note

Untracked `goals/riso-lane-*/**` and `goals/riso-lanes-assurance/**` trees are classified to their owning lane / ASSURANCE. Product payload dirt is under SYS/PY/CLI/PLATFORM primarily.

## Verify snippet

```text
COORD: 19
PY: 26
NODE: 8
SAAS: 8
SYS: 41
DESKTOP: 9
CLI: 18
PLATFORM: 67
ASSURANCE: 24
OUT-OF-SCOPE: 2
TOTAL: 222
unowned: 0
```
