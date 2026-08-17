# W1-C08 — No-legacy policy rewrite (remap then fail-closed)

- Task: `W1-C08`
- Wave: W1
- Date: 2026-08-13
- Repo: `/Users/ww/dev/projects/riso`
- Branch: `main` @ `f7951fe62e7c635f3a90d17811d3711c2a2d7c1b` (no checkout / stash / reset / commit)
- Exclusive writes: `.agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md`, `.agents/skills/riso-release-readiness/SKILL.md`, this file, `residuals/SKILL.md`
- `samples/*/render/**` writes: **0**
- Status: **green** for the policy rewrite; `.claude` skill-mirror copy is residualed (foreign tree)

## Filter / command

```text
rg -n 'do not convert|Do not convert|do-not-convert' .agents/skills/riso-release-readiness
# (empty)

rg -n 'api_tracks|api_language|docs_site|mcp_language|saas_starter_module|saas_auth|saas_billing|include_admin' \
  .agents/skills/riso-release-readiness/references/no-legacy-answer-policy.md
# 8 keys listed (table rows)

uv run python scripts/ci/validate_release_readiness_skill.py
# exit 1 — Skill mirror mismatch: SKILL.md
#          Skill mirror mismatch: references/no-legacy-answer-policy.md
```

## What changed

Old policy listed **5** keys (`api_tracks`, `api_language`, `docs_site`, `mcp_language`, `saas_starter_module`) and said **“Do not convert removed keys into canonical keys.”** That forbade `riso migrate` / `apply_removed_key_remaps`.

New policy:

- Remap the **8** known keys via `apply_removed_key_remaps`, then `reject_removed_answer_keys` leftovers (fail-closed).
- Lists all 8 keys with operator + dest + value rules.
- Removes every “Do not convert” / “do not convert” / “do-not-convert” phrase.
- Still forbids dual-path aliases, dest overwrite, and hidden fallbacks **after** remap.
- `SKILL.md` stop rule no longer blocks remaps; it now stops on leftover dual-path or non-fail-closed leftovers and points at the policy file.

## Eight keys (match `REMOVED_ANSWER_KEYS` / `ANSWER_KEY_REMAPS` / `plan.taskgraph.json` `remap_keys`)

| Old key | Operator | Dest |
| --- | --- | --- |
| `api_tracks` | derive | `api_module`, `api_languages` |
| `api_language` | wrap-list | `api_languages` |
| `docs_site` | derive | `docs_module`, `docs_framework` |
| `mcp_language` | wrap-list | `mcp_languages` |
| `saas_starter_module` | rename | `saas_infra_module` |
| `saas_auth` | split | `saas_auth_module`, `saas_auth_provider` |
| `saas_billing` | split | `saas_billing_module`, `saas_billing_provider` |
| `include_admin` | rename-bool | `saas_admin_dashboard` |

Verify vs plan: 8/8; no “do not convert” in `.agents/skills/riso-release-readiness/**`.

## Handoff (not written this lane)

`.claude/skills/riso-release-readiness/**` is a byte-identical mirror required by `validate_release_readiness_skill.py`. It is **outside** exclusive write root `.agents/skills/riso-release-readiness/**`. Copy is residualed for PL-T07 / SKILL-mirror: see `goals/riso-v2-release-ready/residuals/SKILL.md`.
