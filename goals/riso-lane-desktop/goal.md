# Goal: Riso Lane DESKTOP — Electron and Tauri scaffolds

## Articulated goal

Own the Riso Copier **DESKTOP lane**: exclusive write access to `template/files/electron/**` and `template/files/tauri/**`. Prioritize deep correctness of contracted desktop features (`auto_updater`, `tray_icon`, `custom_titlebar`) and platform packaging on **electron-vite** and **tauri**. Emit COORD handoffs for electron-forge and non-enum feature drift; never invent Copier keys or edit forbidden roots.

## Shared understanding

See [facts.md](./facts.md) for the accepted fact sheet (write roots, feature priority, forge policy, verification bar, hygiene).

Provenance: [interview.json](./interview.json), [facts-review.json](./facts-review.json), [facts.meta.json](./facts.meta.json).

## Execution plan

See [plan.md](./plan.md) — parallel-optimized DESKTOP sub-lanes, hyperfine task graph (waves D0–D6), collision table, handoff schemas, and subagent dispatch templates.

Plan gate status: revised repeatedly for massively parallel subagent execution; treat `plan.md` as the execution authority. Re-run `plannotator annotate goals/riso-lane-desktop/plan.md --gate` and **Approve** if a formal gate receipt is required.

## Done condition

- Enum deep features coherent on electron-vite and tauri scaffolds
- COORD handoffs filed for forge, exclusion-path shape, and non-enum tokens
- `uv run riso validate --answers-file samples/electron-app/copier-answers.yml --json` succeeds
- `uv run riso validate --answers-file samples/tauri-app/copier-answers.yml --json` succeeds
- Jinja validation clean on electron/ and tauri/ when script available
- Optional sample render smoke via official scripts only (no hand-edited `samples/*/render/`)
- No writes outside `template/files/electron/**` and `template/files/tauri/**` (plus goal handoff docs)

## Launch

```text
/goal goals/riso-lane-desktop/goal.md
```
