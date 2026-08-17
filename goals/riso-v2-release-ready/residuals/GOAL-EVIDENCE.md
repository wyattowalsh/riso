# Residual — GOAL-EVIDENCE (W5-CLOSE)

## Summary

CLOSE-GOAL-EVIDENCE rewrote the residual ledger and `ASSURANCE.md` from live commands. Exclusive writes stayed under `goals/riso-v2-release-ready/**`. Refine-stop is **not** claimed green. `render_matrix.py` is **not** residualed.

After official default restore (GATES/PLATFORM), `fact-context-agents` and `fact-release-validators` flipped **green**. Only `fact-refine-stop` remains residual.

## Residuals

### R1 — Review pair still absent

| Field | Value |
| --- | --- |
| **task_id** | W5-CLOSE / RES-GOAL-01 |
| **owner** | Review |
| **status** | open |
| **command** | Write `evidence/W5-R01*` then `evidence/W5-R03*` covering payloads, CLI, wizard, docs, gates with no new P0/P1. Reset the pair if dest smoke P0s (Fumadocs sitemap, Sphinx `make linkcheck`) remain. |
| **blocking reason** | This lane cannot invent the Review pair. Official ladder commands this lane owns are green. Remaining P0/P1s are dest/smoke (see `residuals/GOAL.md` R1). |
| **redacted log** | `ls evidence/W5-R0*` empty. `just validate-agents` 0. Default dest docs smoke still fails `/sitemap.xml`. |
| **fix** | Do not hand-create dests. Do not tag 2.0.0. |
| **evidence** | `evidence/W5-CLOSE-GOAL-EVIDENCE.md` |
