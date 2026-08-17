# Contract delta: `openspec-extra`

Published by **W1-OUT**. OpenSpec is an optional generated extra, **default off**. W2 OPENSPEC / WEB / PLATFORM consume this.

| Field | Value |
| --- | --- |
| **change_id** | `openspec-extra` |
| **applied_at** | 2026-08-13 |
| **status** | `applied` |
| **source_handoff** | `goals/riso-v2-release-ready/evidence/W1-C01-extras.md` |
| **wave** | W1-OUT |
| **repo** | `/Users/ww/dev/projects/riso` (maintainer; branch `main`) |
| **samples/\*/render/\*\* writes** | **0** |

---

## Contract

OpenSpec stays **maintainer-used**. Generated projects get an optional extra that is off by default.

| Surface | Value |
| --- | --- |
| `_defaults.openspec_extra` | `"disabled"` |
| prompt `openspec_extra` | choices `disabled` / `enabled`; default `disabled` |
| `_exclude` | `{% if openspec_extra != 'enabled' %}openspec/{% endif %}` |
| catalog `openspec_extra` | `default_state: disabled`; selected only when extra enabled |
| payload tree | `template/files/openspec/**` **does not exist yet** (OS-T01) |

Omitted `openspec_extra` in sample answers → Copier default `disabled` → `openspec/` excluded.

Do **not** gate `mise.toml` on this extra (see `mise-always`).

---

## Answer keys changed

| key | before | after |
| --- | --- | --- |
| `openspec_extra` | _(absent)_ | new optional extra; default `disabled` |

No new languages, runtimes, or vendors.

---

## Illegal combos now enforced

| rule / condition | location | error message (summary) |
| --- | --- | --- |
| `openspec_extra != 'enabled'` | `copier.yml` `_exclude` | `openspec/` not copied |

---

## Module catalog rows

| name | change |
| --- | --- |
| `openspec_extra` | added; default disabled; optional extra; remap wording in description |
| `quality` | description “ty, not mypy”; deps include `ty` + `mise` |

---

## Context files

| file | action | parity_verified |
| --- | --- | --- |
| `.github/context/quality.md` | update (OpenSpec extra default disabled) | yes (`verify_context_sync.py` exit 0) |
| `template/files/.github/context/quality.md` | update (mirror) | yes |

---

## CLI handoff required

| Field | Value |
| --- | --- |
| **required** | `no` (prompts/catalog already expose the key) |
| **summary** | WEB-T05 store default must be OpenSpec **off**. Do not invent a required sample key. |

COORD (closed after this delta):

- `template/copier.yml` (`openspec_extra` prompt + exclude)
- `template/prompts/**` extras wording
- `template/files/module_catalog.json.jinja` row
- context pair above

---

## Payload checklist

**Do not re-touch COORD paths.**

| lane | exclusive paths to implement | acceptance note | done? |
| --- | --- | --- | --- |
| openspec / coord leftover | `template/files/openspec/**` | OS-T01: optional files; excluded unless `openspec_extra=enabled` | ☐ |
| openspec | default sample | OS-T02: default render/validate has **no** `openspec/` dir | ☐ |
| openspec | throwaway answers `openspec_extra=enabled` | OS-T03: files copy when enabled | ☐ |
| web | `web/src/**` store defaults | WEB-T05: OpenSpec off; `task_runner=just`; no mypy | ☐ |
| platform | `samples/**/copier-answers.yml` | do **not** invent `openspec_extra`; omitted → disabled | ☐ |
| docs | AGENTS / upgrade guide (W4) | mention extra default off | ☐ |

---

## Verification evidence

| stage | command | result |
| --- | --- | --- |
| V2 default | `uv run riso validate --answers-file samples/default/copier-answers.yml --json` | `ok: true` |
| V3 prompts | `uv run riso prompts --json` | `openspec_extra` present; default `disabled` |
| V3 catalog | `uv run riso catalog modules --json` | `ok: true`; row present |
| V1 context | `uv run python scripts/ci/verify_context_sync.py` | `Context directories are in sync.` |
| live tree | `template/files/openspec` | **does not exist** (OS-T01) |

---

## Residual risks

- OS-T01 must add payload files without flipping the default on.
- PLATFORM must not add `openspec_extra: enabled` to samples unless a variant is explicitly that extra.

## Notes

- Never hand-edit `samples/*/render/`.
- Rust / other module excludes are **unchanged** by this CID (SYS-T02).
