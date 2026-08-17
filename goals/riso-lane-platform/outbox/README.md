# PLATFORM outbox

Durable handoffs **from** PLATFORM to owning lanes when investigation shows a non-PLATFORM root cause.

## Rules

- Do not edit foreign trees from PLATFORM.
- Include failing command, redacted log excerpt, suspected paths, requested fix.
- Never paste secrets.

## Template

Copy `_TEMPLATE.md` to `<id>.md` (prefix with owner lane when helpful, e.g. `py-quality-task.md`).
