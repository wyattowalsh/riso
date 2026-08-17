# Contract delta: `mise-always`

Published by **W1-OUT**. Generated `mise.toml` is **always-on** (not an extra). MISE lane fills pins.

| Field | Value |
| --- | --- |
| **change_id** | `mise-always` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-C01-extras.md` (C02) |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

Generated projects always ship `mise.toml`. There is **no** Copier extra and **no** `_exclude` for `mise.toml` or `.mise.toml`.

| Surface | Value |
| --- | --- |
| `template/copier.yml` `_exclude` | comment: “mise.toml and .mise.toml always render (no exclude)” |
| stub | `template/files/mise.toml.jinja` exists (pins are stubs) |
| catalog `mise` | `default_state: enabled`; `selected_state: enabled`; “Not a Copier extra; no toggle” |
| generated Node floor | **20+**; do **not** raise to maintainer **22** |
| maintainer `.mise.toml` | stays `node = "22.23.1"` (MISE-T03; file unchanged unless pin sync required) |

Existing `template/files/.mise.toml.jinja` was left untouched by COORD.

---

## Answer keys changed

| key | before | after |
| --- | --- | --- |
| _(none)_ | mise was not a prompt extra | still not a prompt; always render |

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| _(none)_ | | do not add an exclude or `mise_extra` toggle |

---

## Module catalog rows

| name | change |
| --- | --- |
| `mise` | added always-on row; Node floor 20+ called out |
| `quality` | deps include `mise`; ty not mypy |

---

## Context files

| file | action | parity_verified |
| --- | --- | --- |
| `.github/context/quality.md` | update (“generated `mise.toml` always ships”) | yes |
| `template/files/.github/context/quality.md` | update (mirror) | yes |

---

## CLI handoff required

| Field | Value |
| --- | --- |
| **required** | `no` |
| **summary** | Pin values are MISE lane, not CLI. |

COORD (closed): copier exclude comment + stub file + catalog/context rows.

---

## Payload checklist

**Do not re-touch COORD paths** except MISE exclusive root for pin fill.

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| mise | `template/files/mise.toml.jinja` | MISE-T01: pins python **3.11**, node **20**, pnpm, uv | ☐ |
| mise | same file | MISE-T02: generated Node pin is `20`, **not** 22 | ☐ |
| mise | maintainer `.mise.toml` | MISE-T03: stays Node 22; no floor raise | ☐ |
| mise | `scripts/setup` or generated README | MISE-T04: mention `mise install` once | ☐ |
| py / docs | AGENTS / setup copy | do not document mypy as default; mise always-on | ☐ |
| web | store defaults | no mypy; do not add a mise extra toggle | ☐ |

Stub today:

```toml
[tools]
# stub — MISE lane replaces these pins
```

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| exclude audit | `rg mise.toml template/copier.yml` `_exclude` | no exclude line; comment documents always-on |
| stub | `template/files/mise.toml.jinja` | present; `[tools]` stub |
| maintainer pin | `.mise.toml` | `node = "22.23.1"` |
| V3 catalog | `uv run riso catalog modules --json` | `mise` row enabled |
| V1 context | `uv run python scripts/ci/verify_context_sync.py` | exit 0 |

---

## Residual risks

- Unifying generated Node 20 with maintainer 22 would violate facts. Keep two floors.
- Do not convert mise into an `openspec_extra`-style toggle.

## Notes

- Never hand-edit `samples/*/render/`, `uv.lock`, or `pnpm-lock.yaml`.
