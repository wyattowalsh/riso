# Feature Specification: Changelog & Release Management

**Feature Branch**: `014-changelog-release-management`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Conventional commits enforcement, automatic changelog generation (semantic-release). Features: semantic versioning automation, GitHub Releases, breaking change detection, migration guides. Release artifact publishing (PyPI, npm, Docker Hub). Note: Release process completes in <10 minutes target"

## Clarifications

### Session 2025-11-02

- Q: How should Git hooks be installed and maintained across developer environments? → A: Automatic installation via post-clone script with manual fallback (uv/pnpm scripts)
- Q: How should registry credentials be stored and rotated to balance security with operational simplicity? → A: GitHub Secrets with annual rotation reminder (documented in README)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Commit Format Enforcement (Priority: P1)

Developers commit code changes following a standardized commit message format. The system validates commit messages at commit time and prevents non-compliant commits from being accepted. This ensures all commits are machine-readable and can drive automated changelog generation.

**Why this priority**: Foundation for all automated release features. Without standardized commits, no downstream automation is possible. Delivers immediate value by improving team communication and commit history quality.

**Independent Test**: Can be fully tested by attempting commits with various message formats (valid and invalid) and verifying enforcement works. Delivers value through improved commit history clarity and team communication standards.

**Acceptance Scenarios**:

1. **Given** a developer attempts to commit code, **When** the commit message follows conventional format (e.g., "feat: add user login"), **Then** the commit is accepted
2. **Given** a developer attempts to commit code, **When** the commit message does not follow format (e.g., "fixed stuff"), **Then** the commit is rejected with helpful error message explaining the format
3. **Given** a developer uses a Git GUI or CLI, **When** committing, **Then** they receive immediate feedback on commit message validity

---

### User Story 2 - Automatic Changelog Generation (Priority: P1)

When a release is triggered, the system automatically generates a human-readable changelog from commit history. The changelog categorizes changes by type (features, fixes, breaking changes) and includes links to commits and pull requests. Users can understand what changed between versions without manually reading commit history.

**Why this priority**: Core value delivery - eliminates manual changelog maintenance burden and provides users with clear release documentation. This is the primary output that justifies standardized commits.

**Independent Test**: Can be fully tested by creating commits with various types (feat, fix, breaking) and verifying the generated changelog correctly categorizes and formats them. Delivers value through automated release notes.

**Acceptance Scenarios**:

1. **Given** commits exist with types `feat`, `fix`, and `chore`, **When** changelog is generated, **Then** features and fixes appear in separate sections, chores are excluded
2. **Given** a commit with `BREAKING CHANGE` footer, **When** changelog is generated, **Then** breaking changes are prominently highlighted in a dedicated section
3. **Given** commits reference pull request numbers, **When** changelog is generated, **Then** links to those PRs are included
4. **Given** commits span multiple versions, **When** generating changelog for a specific version, **Then** only commits since the previous version are included

---

### User Story 3 - Semantic Version Automation (Priority: P1)

The system automatically determines the next version number based on commit types. Feature commits trigger minor version bumps, fixes trigger patch bumps, and breaking changes trigger major version bumps. Version numbers follow semantic versioning (MAJOR.MINOR.PATCH) without manual intervention.

**Why this priority**: Removes human error and decision-making from versioning. Combined with commit enforcement and changelog generation, completes the MVP automated release workflow.

**Independent Test**: Can be fully tested by creating commit sequences and verifying correct version bump calculation. Delivers value through consistent, predictable version numbers.

**Acceptance Scenarios**:

1. **Given** only `fix` commits since last release, **When** calculating next version, **Then** PATCH version increments (e.g., 1.2.3 → 1.2.4)
2. **Given** at least one `feat` commit since last release, **When** calculating next version, **Then** MINOR version increments and PATCH resets (e.g., 1.2.3 → 1.3.0)
3. **Given** at least one breaking change commit, **When** calculating next version, **Then** MAJOR version increments and MINOR/PATCH reset (e.g., 1.2.3 → 2.0.0)
4. **Given** no qualifying commits since last release, **When** attempting to release, **Then** no release is created

---

### User Story 4 - GitHub Release Creation (Priority: P2)

When a new version is created, the system automatically creates a GitHub Release with the version number as the tag, the changelog content as the release notes, and marks breaking change releases appropriately. Users and automated systems can discover new releases through GitHub's release mechanism.

**Why this priority**: Extends changelog generation with distribution mechanism. Not critical for MVP but highly valuable for discoverability and integration with GitHub ecosystem.

**Independent Test**: Can be fully tested by triggering a release and verifying GitHub Release creation with correct tag, notes, and metadata. Delivers value through standardized release distribution.

**Acceptance Scenarios**:

1. **Given** a new version is released, **When** the release completes, **Then** a GitHub Release is created with version tag (e.g., `v1.2.3`)
2. **Given** a new version with changelog content, **When** GitHub Release is created, **Then** the release notes contain the formatted changelog
3. **Given** a release with breaking changes, **When** GitHub Release is created, **Then** the release is marked as a major version with breaking change warnings
4. **Given** a pre-release version (e.g., beta), **When** GitHub Release is created, **Then** it is marked as a pre-release

---

### User Story 5 - Breaking Change Detection & Migration Guides (Priority: P2)

The system detects breaking changes from commit messages and generates migration guide templates. Developers can add migration instructions that appear prominently in changelogs and release notes. Users upgrading across breaking changes receive clear guidance on required actions.

**Why this priority**: Enhances breaking change communication beyond simple detection. Important for mature projects but not required for basic release automation.

**Independent Test**: Can be fully tested by creating commits with breaking changes and verifying detection, changelog prominence, and migration guide generation. Delivers value through improved upgrade experience.

**Acceptance Scenarios**:

1. **Given** a commit with `BREAKING CHANGE` in body or footer, **When** validating commit, **Then** the commit is flagged as breaking
2. **Given** breaking change commits, **When** generating changelog, **Then** breaking changes appear first with prominent formatting
3. **Given** a breaking change commit with migration notes, **When** generating changelog, **Then** migration instructions are included
4. **Given** multiple breaking changes in one release, **When** generating changelog, **Then** all breaking changes are listed with individual migration guides

---

### User Story 6 - Release Artifact Publishing (Priority: P3)

After version and changelog generation, the system can publish release artifacts to package registries (PyPI for Python, npm for JavaScript, Docker Hub for containers). Publishing is triggered automatically on successful release or manually initiated. Users can install the newly released version from standard package sources.

**Why this priority**: Distribution automation - valuable but depends on successful core release workflow. Can be added incrementally per registry type.

**Independent Test**: Can be fully tested by triggering release and verifying package appears in target registry with correct version. Delivers value through automated distribution.

**Acceptance Scenarios**:

1. **Given** a Python project with PyPI credentials configured, **When** a release completes, **Then** the package is published to PyPI with the new version
2. **Given** a Node.js project with npm credentials configured, **When** a release completes, **Then** the package is published to npm with the new version
3. **Given** a project with Docker Hub credentials configured, **When** a release completes, **Then** container images are pushed with version tags (e.g., `v1.2.3`, `v1.2`, `v1`, `latest`)
4. **Given** publishing fails due to credentials or network issues, **When** the error occurs, **Then** the release process reports the failure and allows manual retry

---

### Edge Cases

- What happens when a commit has multiple types (e.g., both feat and fix)? → System should prioritize the highest significance type (breaking > feat > fix)
- How does system handle manual version bumps or out-of-sequence versions? → Should validate semantic versioning consistency and warn on anomalies
- What if a developer needs to bypass commit format for emergency hotfixes? → Provide override mechanism with justification requirement and audit logging
- How are dependency updates handled in changelog? → Can be configured to include/exclude based on commit type (e.g., `chore(deps)`)
- What if GitHub API is unavailable during release? → Should retry with exponential backoff and allow manual completion
- How to handle multiple releases in rapid succession? → Queue releases and process sequentially to prevent conflicts
- What if changelog generation fails mid-release? → Should rollback version tag and fail gracefully with detailed error message

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST enforce conventional commit message format at commit time (types: feat, fix, docs, chore, refactor, test, breaking)
- **FR-002**: System MUST validate commit message structure (type, optional scope, description, optional body, optional footer)
- **FR-003**: System MUST detect breaking changes from commit message footers or body containing "BREAKING CHANGE"
- **FR-004**: System MUST automatically calculate next semantic version based on commit types since last release
- **FR-005**: System MUST generate changelog content categorized by change type (breaking changes, features, fixes)
- **FR-006**: System MUST include commit references and pull request links in changelog entries
- **FR-007**: System MUST create GitHub Release with version tag, changelog content, and appropriate metadata
- **FR-008**: System MUST mark breaking change releases prominently in changelog and release notes
- **FR-009**: System MUST support migration guide templates for breaking changes
- **FR-010**: System MUST publish artifacts to configured package registries (PyPI, npm, Docker Hub) with correct version tags
- **FR-011**: System MUST support both automated release triggers (on merge to main) and manual release initiation via GitHub Actions workflow_dispatch UI or `gh workflow run release.yml` CLI
- **FR-012**: System MUST provide configuration for release process (commit types, changelog sections, publishing targets)
- **FR-013**: System MUST complete full release process (version calculation, changelog, release creation, publishing) in under 10 minutes
- **FR-014**: System MUST validate semantic version consistency and prevent invalid version jumps
- **FR-015**: System MUST support dry-run mode for testing release process without actual publishing (includes version calculation, changelog generation, and registry API connectivity checks, but skips actual artifact publishing and GitHub Release creation)
- **FR-016**: System MUST provide detailed logging of release process steps for debugging (JSON-structured logs with INFO/DEBUG/ERROR levels, output to stdout and `.riso/logs/release-{timestamp}.log`, 30-day retention, include correlation IDs for tracing multi-step operations)
- **FR-017**: System MUST handle multiple package types in monorepo scenarios (independent versioning per package)
- **FR-018**: System MUST support pre-release versions (alpha, beta, rc) with appropriate tagging
- **FR-019**: System MUST document registry credential rotation schedule (annual) in generated project README with setup instructions

### Key Entities

- **Commit Message**: Structured text following conventional format, contains type, scope (optional), description, body (optional), footer (optional), breaking change flag
- **Version**: Semantic version number (MAJOR.MINOR.PATCH), calculated from commit history, tagged in Git and applied to artifacts
- **Changelog**: Generated document categorizing changes by type, contains version header, change sections (breaking/features/fixes), commit references, PR links
- **Release**: GitHub Release entity, contains version tag, changelog as release notes, artifact attachments, pre-release flag
- **Release Configuration**: Settings defining commit types, changelog sections, registry credentials, publishing targets, monorepo package mappings
- **Migration Guide**: Documentation for breaking changes, contains old behavior description, new behavior description, upgrade steps, code examples

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can commit code with validated conventional format enforcement, preventing 100% of non-compliant commits from entering main branch
- **SC-002**: Changelog generation completes in under 30 seconds for repositories with up to 1000 commits since last release
- **SC-003**: Version calculation accuracy is 100% based on commit types (no incorrect major/minor/patch bumps)
- **SC-004**: Full release process from trigger to published artifacts completes in under 10 minutes for projects with 3 or fewer package registries
- **SC-005**: Breaking changes are detected and highlighted in 100% of releases containing breaking commits
- **SC-006**: Release notes are automatically populated in GitHub Releases, eliminating manual changelog writing for 100% of releases
- **SC-007**: Published packages appear in target registries within 2 minutes of successful release
- **SC-008**: Developers can identify release process failures within 1 minute through clear error messages and logs
- **SC-009**: Teams report significant subjective improvement in release management efficiency after 30 days of usage (target: 80% of surveyed team members rate release process as "Much Faster" or "Significantly Easier" compared to previous manual workflow)
- **SC-010**: Zero release rollbacks due to versioning errors in first 90 days after implementation

## Assumptions

1. **Commit Format Adoption**: Assumes team will adapt to conventional commit format with reasonable onboarding period (suggest 2-week grace period with warnings before enforcement)
2. **GitHub Platform**: Assumes projects use GitHub for repository hosting and GitHub Actions for CI/CD
3. **Registry Credentials**: Registry credentials stored as GitHub Secrets with annual rotation reminder documented in project README; credentials include PyPI API tokens, npm authentication tokens, and Docker Hub access tokens
4. **Semantic Versioning**: Assumes projects follow semantic versioning principles and understand MAJOR.MINOR.PATCH significance
5. **Linear History Preference**: Assumes merge commits or squash merges to main branch (not individual commits from PR branches)
6. **Release Frequency**: Assumes release frequency of at least weekly for optimal automation value
7. **Breaking Change Communication**: Assumes developers document breaking changes appropriately in commit messages or PR descriptions
8. **Monorepo Tooling**: For monorepo scenarios, assumes use of conventional tooling (Lerna, Nx, or similar) for package management

## Dependencies

- **Existing Feature 004 (GitHub Actions Workflows)**: Requires CI/CD infrastructure for automated release triggers
- **Existing Feature 005 (Container Deployment)**: For Docker Hub publishing capability
- **Existing Template Infrastructure**: Requires Copier template rendering and hooks for integration
- **Git Hooks Support**: Git commit-msg hook installed automatically via post-clone script (uv/pnpm run setup) with manual fallback; hook validates commit messages locally before push
- **GitHub API Access**: Requires GitHub personal access token or GitHub App with Releases write permission
- **Package Registry Accounts**: Requires accounts and credentials for target registries (PyPI, npm, Docker Hub)

## Out of Scope

- Custom commit message formats beyond conventional commits specification
- Changelog content editing or manual override after generation
- Release approval workflows or staging environments (assumes direct releases)
- Changelog translation or internationalization
- Advanced monorepo features like cross-package dependency analysis
- Release rollback automation (manual rollback process acceptable)
- Integration with project management tools (Jira, Linear) for ticket linking
- Custom version numbering schemes (non-semantic versioning)
- Changelog generation for historical versions (only prospective from implementation forward)
