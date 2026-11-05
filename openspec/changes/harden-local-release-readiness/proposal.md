## Why

Fresh source review found release blockers that the passing maintainer suite does
not exercise: sample path traversal, external hook execution, tenant context
leakage, invalid generated admin components, and lossy wizard imports. Historical
matrix results and the disconnected local/remote Git histories cannot establish
current release readiness.

## What Changes

- Constrain sample regeneration to canonical sample destinations before deletion.
- Isolate tenant context per request and require admin authorization before reads.
- Preserve valid imported wizard answers and reject malformed external state.
- Keep CLI validation and failed update operations free of unintended writes.
- Verify installed package behavior, generated runtime contracts, docs, and gates.
- Apply the approved workflow and trusted-hook corrections, then merge both main
  histories, verify the combined tree, and update remote main as requested.

## Capabilities

### New Capabilities

- `local-release-assurance`: Safety and evidence requirements for CLI operations,
  generated SaaS code, wizard interchange, and downstream sample refreshes.

### Modified Capabilities

None; this repository has no existing OpenSpec capability specifications.

## Impact

`src/riso`, SaaS template files, sample automation, wizard state/interchange,
focused regression tests, release documentation, and generated matrix snapshots.
No new runtime dependencies, new sample variants, release publishing, or credentials
are required. Existing dev dependencies are restored and security findings patched.
The maintainer approved the hook/CI changes and subsequent main history merge and
remote synchronization; history rewriting remains outside scope.
