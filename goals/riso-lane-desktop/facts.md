# Facts

- This lane may write only under template/files/electron/** and template/files/tauri/**.
- This lane does not edit copier.yml, hooks, macros, module_catalog, other language trees, src/riso, web, samples answers, or samples/*/render/.
- This lane does not invent new Copier answer keys; contract changes are COORD handoffs only.
- Primary work prioritizes deep feature correctness for auto_updater, tray_icon, and custom_titlebar across Electron and Tauri scaffolds.
- Electron templates gate correctly on desktop_module=enabled and desktop_framework=electron-vite, with feature and platform conditionals for updater, tray, titlebar, and mac/windows/linux packaging.
- Tauri templates gate correctly on desktop_module=enabled and desktop_framework=tauri, with coherent auto_updater, tray_icon, custom_titlebar, packaging, entitlements/capabilities, and updater wiring.
- Non-enum desktop feature gates (e.g. system_info, menu in Tauri) are aligned to the existing desktop_features enum where safe, and a COORD handoff is written for remaining contract decisions.
- electron-forge is not scaffolded until COORD agrees; this lane emits a COORD handoff covering missing forge tree and exclusion-path shape (copier references electron/electron-forge/ while the tree is flat electron-vite).
- If COORD approves the forge contract/exclusion shape, this lane may implement an electron-forge scaffold still confined to template/files/electron/**.
- Desktop renderer/UI code stays local to electron/ and tauri/; this lane does not take ownership of template/files/frontend/** or node/saas/**.
- samples/electron-app/copier-answers.yml validates successfully via uv run riso validate --answers-file ... --json.
- samples/tauri-app/copier-answers.yml validates successfully via uv run riso validate --answers-file ... --json.
- Jinja under electron/ and tauri/ passes uv run python scripts/ci/validate_jinja_templates.py when that script is available.
- Electron and Tauri sample renders can be regenerated via render scripts (not hand-edited) for smoke evidence when needed.
- samples/*/render/ is never hand-edited; regeneration uses official render scripts only.
- No branches, worktrees, commits, or pushes unless the human explicitly asks; no lockfile hand-edits; no secrets committed, printed, or persisted.
