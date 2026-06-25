# Plan: Production Release Readiness

## Goal

Make Riso release-candidate ready without publishing, tagging, pushing, or
preserving stale legacy answer behavior.

## Workstreams

1. **Schema and hooks**: enforce canonical answer keys, reject removed keys,
   remove post-generation pre-commit installation side effects, and keep render
   metadata canonical.
1. **Samples and automation**: migrate checked sample answer files, update
   render metadata, and regenerate renders only through automation.
1. **MCP and web**: expose canonical answer dictionaries through public MCP
   tools/resources/prompts and the web configurator.
1. **Docs and skills**: keep docs warning-free, add release-readiness spec
   artifacts, and add the maintainer-only release skill.
1. **CI and release**: make package builds blocking, align pnpm, add package
   metadata and install smoke checks, and preserve dry-run-only release proof.
1. **Security and hygiene**: remove generated artifacts, scan for secrets, audit
   dependencies, and record evidence in the release TODO.

## Non-Goals

- No legacy answer conversion.
- No generated sample render hand edits.
- No publish, tag, push, commit, branch switch, stash, reset, or rebase.
- No maintainer release skill in rendered project payloads.

## Release Candidate Criteria

- No active references to removed answer keys outside negative tests and release
  notes explaining rejection.
- Sphinx docs build with `-W`.
- Focused and full Python tests pass with required dependency groups.
- Web lint, tests, build, and e2e gates pass.
- Render matrix completes for supported sample variants.
- Package build, metadata check, wheel install smoke, and release dry-run pass.
- Security scans either pass or have fixed findings.
