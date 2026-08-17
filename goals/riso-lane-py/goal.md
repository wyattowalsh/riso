# Goal — Riso Lane PY

## Articulated goal

Make the Riso Copier **Python payload** under `template/files/python/**` correct, feature-gated, and maintainable for multi-agent work: exclusive PY-lane ownership for packaging, FastAPI, Typer CLI, FastMCP, GraphQL/WebSocket, Sphinx docs, shipped tests, codegen, and release helpers—without editing COORD contracts or other language/product trees.

## Shared understanding

See [`facts.md`](./facts.md) (authoritative acceptance criteria).

## Execution plan

See [`plan.md`](./plan.md) (Plannotator-approved). Parallel sub-lanes with serial integration on shared hotspots; COORD handoffs under [`handoffs/`](./handoffs/) when contracts must change.

## Done when

- Jinja under `template/files/python/**` is valid for relevant answer combinations
- Feature-gated content is correct when enabled and does not break when siblings are off
- Verification: `validate_jinja_templates.py` + `riso validate` on python-heavy samples + narrow maintainer pytest
- COORD handoffs listed for any contract gaps
- No writes outside `template/files/python/**` (except this goal package)
- No unauthorized git ops, lockfile edits, secrets, or hand-edits of `samples/*/render/`

## Launch

```text
/goal goals/riso-lane-py/goal.md
```
