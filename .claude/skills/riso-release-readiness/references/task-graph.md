# Task Graph

## Parallel Lanes

- **Template**: `template/copier.yml`, answer validation, generated answer file.
- **Hooks**: `template/hooks/**`, post-gen metadata, cleanup behavior.
- **Samples**: checked `samples/**/copier-answers.yml`; never hand-edit renders.
- **MCP**: `src/riso/mcp/**`, MCP public docs, MCP tests.
- **Web**: `web/**`, wizard state, validation, presets, build/test gates.
- **Docs**: `docs/**`, template docs mirrors, Sphinx warnings.
- **CI/Release**: `.github/workflows/**`, package metadata, pnpm/mise alignment.
- **Security**: audits, generated artifacts, secret scan, final diff review.

## Coordination Rules

- Assign exactly one owner per same-file edit surface.
- Run independent read-only audits in parallel.
- Run generated surfaces only after source changes land.
- Run broad validation only after focused gates pass.
- Final synthesis belongs to the coordinator.
