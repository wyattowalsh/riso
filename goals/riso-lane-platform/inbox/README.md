# PLATFORM inbox

Inbound work signals for the PLATFORM lane. Drop structured handoffs here; do not invent Copier keys.

## Accepted sources

- COORD outbox contract deltas (`goals/riso-lane-coord/outbox/`)
- Payload-lane handoffs (PY / NODE / SAAS / SYS / DESKTOP / CLI)
- CI failures in PLATFORM write roots
- Human-promoted notes (explicit)

## How to file

Copy `_TEMPLATE.md` to `<id>.md` and fill every section.
