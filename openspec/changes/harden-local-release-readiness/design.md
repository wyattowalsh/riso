## Context

Baseline `just quality` passes 1154 tests with nine platform/tool skips. Web unit
tests pass 308 tests, but the production build fails on missing Node type imports.
Sphinx builds without warnings. Source audits demonstrate defects outside these
gates. Local main and fetched origin/main have no common merge base; patch
equivalence leaves 44 local and 72 upstream commits, so automatic pull is unsafe.

## Goals / Non-Goals

Goals: close reproduced security and answer-preservation defects; add behavioral
regressions; regenerate derived outputs only through owning automation; report
the exact scope and freshness of each check.

Non-goals: publish a release, change credentials or installed harness preferences,
rewrite Git history, upgrade all dependency majors, or claim unavailable
external/platform checks passed.

The maintainer subsequently requested merging both main histories locally,
assuring the combined tree, and updating remote main. Preserve both histories in
a normal merge; no reset, rebase, new branch, or forced push is needed.

## Decisions

- Canonicalize and validate sample paths before destructive work; reject traversal
  components, mismatched answers/destinations, and escaping symlinks.
- Replace singleton tenant mutation with AsyncLocalStorage run scopes. Protected
  operations in strict mode fail without a tenant; explicit excluded models keep
  their documented behavior.
- Keep server authorization/data access separate from interactive client pages.
- Validate external wizard configuration after removed-key remapping and before
  state mutation. Apply imported/shared selections atomically over defaults.
- Defer answer persistence until validation and template operations succeed.
- Reconcile both main histories using shared historical file contents where
  available and review semantic conflicts against the hardened contracts.
- Bound source archives to installable package assets, and test actual copy and
  recopy from a wheel outside the checkout so bundled hooks resolve their helpers.
- Keep workflow and generation-hook changes reviewable before asking for their
  repository-required approval. No gate becomes advisory merely to pass.

## Risks / Trade-offs

AsyncLocalStorage is a Node server runtime API; the affected tenancy implementation
must stay server-side. Full generated builds require their own dependencies and
toolchains. Render-only checks, if used, must be identified as render evidence,
never smoke/build evidence. Existing sample metadata stays historical until an
owning render command refreshes it.

## Validation

Focused regressions precede full maintainer/web checks. Validate all official
answer files, Jinja syntax, mirror/context parity, strict docs builds, installed
package behavior, and representative generated runtime builds. Capture command
exits and unresolved release gates in the local release evidence record.
