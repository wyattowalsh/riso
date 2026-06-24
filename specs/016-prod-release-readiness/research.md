# Research: Production Release Readiness

## Scope

This change prepares Riso for a release-candidate handoff across the active
repo surfaces: Copier schema, hooks, samples, MCP APIs, web wizard, docs,
workflows, packaging, generated artifacts, and maintainer skills.

## Decisions

### Copier Answers

- **Decision**: Use only component-first answer keys.
- **Canonical keys**: `api_module`, `api_languages`, `docs_module`,
  `docs_framework`, `mcp_module`, `mcp_languages`, `saas_infra_module`.
- **Rejected option**: legacy aliases or fallback conversion for `api_tracks`,
  `api_language`, `docs_site`, `mcp_language`, or `saas_starter_module`.
- **Reason**: current code plus maintainer direction is the source of truth;
  version control is the rollback path for unshipped behavior.

### Release Gates

- **Decision**: release-critical checks are blocking by default.
- **Blocking gates**: schema validation, focused tests, docs `-W`, render
  matrix, Python quality, web quality, package build, metadata check, wheel
  install smoke, release dry-run, and security scans.
- **Reason**: non-blocking release gates mask production readiness failures.

### Package Publishing

- **Decision**: produce a release candidate and dry-run evidence only.
- **Actual publishing**: requires explicit maintainer approval and trusted
  publisher configuration verification.
- **Reason**: publish/tag/push are external-state mutations outside normal
  release-readiness implementation.

### Agent Skills

- **Decision**: add a maintainer-only `riso-release-readiness` skill.
- **Placement**: `.agents/skills/riso-release-readiness` is the source of truth;
  `.claude/skills/riso-release-readiness` mirrors it for Claude Code.
- **Excluded**: rendered projects do not receive this skill.
- **Reason**: the workflow is for maintaining Riso itself, not for projects
  generated from the template.

### Documentation

- **Decision**: docs must build with Sphinx warnings treated as errors.
- **Required fixes**: every source page is in a toctree or intentionally
  excluded, MyST links resolve or become literal paths, and XML-like prompt
  examples use non-XML fences.
- **Reason**: warnings-as-errors is the only reliable local release docs gate.

## External References

- Copier configuration and answers: <https://copier.readthedocs.io/en/stable/configuring/>
- uv package build and publish workflow: <https://docs.astral.sh/uv/guides/package/>
- semantic-release configuration and dry-run: <https://semantic-release.org/usage/configuration>
- Sphinx toctree and warning behavior: <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>
- pnpm frozen installs: <https://pnpm.io/cli/install>
- PyPI Trusted Publishing: <https://docs.pypi.org/trusted-publishers/using-a-publisher/>
- Agent Skills specification: <https://agentskills.io/specification>
- Codex skills: <https://developers.openai.com/codex/skills>
- Claude Code skills: <https://code.claude.com/docs/en/skills>

