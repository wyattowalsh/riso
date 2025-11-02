# Feature Specification: Conventional Commit Tooling Integration

**Feature Branch**: `016-conventional-commit-tooling`  
**Created**: 2025-11-02  
**Status**: Draft  
**Input**: User description: "Integrate commit message validation and guided authoring tools for conventional commit format across Python and Node.js projects"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Commit Message Validation (Priority: P1)

As a developer committing code to a Riso-templated project, I need my commit messages automatically validated against conventional commit standards so that the project maintains a clean, parseable commit history for automated changelog generation.

**Why this priority**: This is the foundation for automated versioning and changelog generation. Without validated commits, semantic-release cannot function correctly. This is the MVP feature that delivers immediate value by catching malformed commits before they reach the repository.

**Independent Test**: Can be fully tested by making a commit with an invalid message (e.g., "fixed bug") and verifying the commit is rejected with a helpful error message, then making a valid commit (e.g., "fix: resolve login timeout") and verifying it succeeds.

**Acceptance Scenarios**:

1. **Given** a developer has cloned a Riso project with commit validation enabled, **When** they attempt to commit with message "fixed some stuff", **Then** the commit is rejected with an error showing the correct format and examples
2. **Given** a developer has cloned a Riso project, **When** they commit with message "feat(api): add user authentication endpoint", **Then** the commit succeeds and the message is recorded in git history
3. **Given** a developer has cloned a Riso project, **When** they commit with message "feat!: migrate to new database schema", **Then** the commit succeeds and the breaking change indicator is captured
4. **Given** a developer attempts to commit with an invalid type, **When** they use message "featrue: add endpoint", **Then** they receive an error listing valid types (feat, fix, docs, style, refactor, test, chore)
5. **Given** a developer needs to bypass validation in an emergency, **When** they use `git commit --no-verify`, **Then** the commit succeeds without validation

---

### User Story 2 - Guided Commit Message Authoring (Priority: P2)

As a developer new to conventional commits or working on a complex change, I need an interactive CLI tool that guides me through creating properly formatted commit messages so that I don't have to memorize the format or risk making mistakes.

**Why this priority**: While validation (P1) catches errors, guided authoring prevents them. This improves developer experience significantly by reducing friction and cognitive load, but the project can function with just validation if needed.

**Independent Test**: Can be fully tested by running the commit authoring command, following the interactive prompts to select type, scope, and description, and verifying the generated commit message matches conventional commit format.

**Acceptance Scenarios**:

1. **Given** a developer has staged changes, **When** they run the guided commit command, **Then** they are prompted to select a commit type from a list (feat, fix, docs, etc.)
2. **Given** a developer is authoring a commit, **When** they select a type, **Then** they are prompted for an optional scope with helpful examples
3. **Given** a developer is authoring a commit, **When** they complete type and scope, **Then** they are prompted for a short description with character limit guidance (max 72 chars)
4. **Given** a developer is authoring a commit, **When** they complete the short description, **Then** they can optionally add a longer body description
5. **Given** a developer is authoring a breaking change, **When** they indicate this in the CLI, **Then** they are prompted to describe the breaking change details
6. **Given** a developer completes the guided flow, **When** they confirm the commit, **Then** the commit is created with properly formatted conventional message

---

### User Story 3 - Cross-Platform Hook Installation (Priority: P1)

As a developer setting up a Riso project on any operating system (macOS, Linux, Windows), I need Git hooks automatically installed during project setup so that commit validation works immediately without manual configuration.

**Why this priority**: Without automatic hook installation, developers must manually copy files to `.git/hooks/`, leading to inconsistent enforcement across team members. This is part of the MVP since validation (P1) depends on hooks being installed.

**Independent Test**: Can be fully tested by running the project setup command on a fresh clone and verifying that the commit validation hook is installed and executable, then testing that commit validation works.

**Acceptance Scenarios**:

1. **Given** a developer has just cloned a Riso project, **When** they run the setup-hooks command, **Then** the commit-msg hook is copied to `.git/hooks/` and made executable
2. **Given** a developer runs the setup script on Windows, **When** the hook is installed, **Then** it works correctly (Python-based, no Bash requirement)
3. **Given** a developer runs the setup script multiple times, **When** hooks already exist, **Then** the script reports "already installed" without error
4. **Given** a developer wants to verify hook installation, **When** they check `.git/hooks/commit-msg`, **Then** the file exists and contains the validation logic
5. **Given** a developer needs to uninstall hooks, **When** they delete `.git/hooks/commit-msg`, **Then** validation no longer runs (clean uninstall)

---

### User Story 4 - Python-Only Project Support (Priority: P2)

As a maintainer of a Python-only Riso project, I need commit tooling that works without requiring Node.js installation so that my project dependencies remain minimal and aligned with the Python ecosystem.

**Why this priority**: Many Riso projects are Python-only and shouldn't require Node.js for commit validation. This expands the tool's applicability but isn't required for the core MVP (Node.js projects work fine with standard tooling).

**Independent Test**: Can be fully tested by rendering a Python-only Riso project (no Node.js dependencies), running hook installation, and verifying commits are validated without any Node.js installation present on the system.

**Acceptance Scenarios**:

1. **Given** a Python-only Riso project, **When** hooks are installed, **Then** validation runs via the project's Python environment
2. **Given** a Python-only project, **When** a developer commits, **Then** validation works without requiring Node.js
3. **Given** a Python-only project, **When** hook installation fails due to missing Node.js, **Then** a fallback mechanism uses Python-based validation
4. **Given** a Python-only project, **When** checking dependencies, **Then** only Python packages are listed, not Node.js packages

---

### User Story 5 - Configuration Customization (Priority: P3)

As a project maintainer, I need to customize commit types, scopes, and validation rules so that the tooling matches my project's specific conventions and domain terminology.

**Why this priority**: While standard conventional commit types (feat, fix, docs, etc.) work for most projects, some teams have specific needs (e.g., adding "perf" type, custom scopes for monorepo packages). This is valuable but not essential for initial adoption.

**Independent Test**: Can be fully tested by editing the configuration file to add a custom type (e.g., "perf"), committing with that type, and verifying validation passes. Then test with an undefined type to ensure validation still catches errors.

**Acceptance Scenarios**:

1. **Given** a project maintainer wants custom commit types, **When** they edit the configuration file to add types, **Then** validation accepts the new types
2. **Given** a monorepo project, **When** maintainer defines package scopes in config, **Then** the guided authoring tool shows only valid scopes
3. **Given** a project needs stricter rules, **When** maintainer enables additional rules (e.g., subject case, max length), **Then** validation enforces them
4. **Given** a project uses custom footer keywords, **When** maintainer configures them, **Then** commits with those footers are validated correctly

---

### Edge Cases

- **What happens when a developer clones a project but never runs the setup-hooks command?** The hook won't be installed, and commits won't be validated. The README must clearly document this setup step, and CI validation should catch invalid commits before merge.

- **How does the system handle merge commits generated by GitHub/GitLab?** Merge commits typically have format "Merge pull request #123" which doesn't follow conventional commit format. The validation should skip merge commits by checking for "Merge" prefix.

- **What happens when a developer amends a commit that was created before hooks were installed?** The hook runs on the amended commit message. If the original message was invalid, validation fails. Developer must rewrite to conventional format or use --no-verify.

- **How does tooling work in CI environments where Git hooks don't exist?** CI validation runs the validation tool directly on commit messages, not via hooks. The workflow checks all commits in a PR against conventional commit rules.

- **What happens when validation tool config conflicts with guided authoring prompts?** This is a configuration error. The template must ensure both tools use the same configuration so prompts match validation rules.

- **How does system handle commits from external contributors who don't have hooks installed?** PR validation workflow runs validation on all commits before merge. Invalid commits are flagged in PR checks with instructions for fixing.

- **What happens on systems where scripts aren't executable by default (Windows)?** The hook uses appropriate script headers and Git automatically invokes via the correct interpreter. No execute permission needed on Windows.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate all commit messages against conventional commit format (type(scope): subject) before accepting commits
- **FR-002**: System MUST support standard conventional commit types: feat, fix, docs, style, refactor, test, chore
- **FR-003**: System MUST detect breaking changes indicated by "!" after type/scope or "BREAKING CHANGE:" in footer
- **FR-004**: System MUST reject commits with invalid format and display helpful error messages with examples
- **FR-005**: System MUST allow developers to bypass validation using `git commit --no-verify` flag
- **FR-006**: System MUST provide an interactive CLI tool for guided commit message authoring
- **FR-007**: Guided authoring tool MUST prompt for: commit type, optional scope, short description, optional body, optional footer
- **FR-008**: Guided authoring tool MUST enforce character limits (72 chars for subject line)
- **FR-009**: System MUST support automatic Git hook installation via setup script
- **FR-010**: Hook installation MUST work on macOS, Linux, and Windows without requiring bash
- **FR-011**: System MUST support Python-only projects without requiring Node.js installation
- **FR-012**: System MUST support Node.js projects using standard tooling
- **FR-013**: System MUST allow configuration customization via version-controlled configuration files
- **FR-014**: Configuration MUST allow custom types, scopes, and validation rules
- **FR-015**: System MUST skip validation for merge commits (starting with "Merge ")
- **FR-016**: System MUST provide CI workflow integration for validating commits in pull requests
- **FR-017**: CI validation MUST check all commits in a PR, not just the merge commit
- **FR-018**: System MUST log validation failures with specific rule violations and line numbers
- **FR-019**: Hook installation script MUST detect existing hooks and report status without error
- **FR-020**: System MUST store configuration in version-controlled files (not environment variables)

### Key Entities *(include if feature involves data)*

- **Commit Message**: Git commit message text with three parts: header (type, scope, subject), optional body, optional footer. Header limited to 72 chars, body wrapped at 72 chars.

- **Validation Rule**: Configuration defining allowed types, scopes, subject patterns, and constraints. Stored in version-controlled configuration files with rule name, severity level (error/warning), and optional parameters.

- **Hook Script**: Executable file in Git hooks directory that receives commit message as input and returns success or failure. Must be cross-platform compatible.

- **Commit Type**: Categorical value indicating change category (feat, fix, docs, style, refactor, test, chore). Maps to semantic version bumps (feat→minor, fix→patch, BREAKING CHANGE→major).

- **Commit Scope**: Optional namespace indicating affected area (e.g., "api", "cli", "docs"). In monorepo, typically matches package name.

- **Configuration Profile**: Set of validation rules and tool settings. Template provides "standard" (default) and "strict" (enhanced rules) profiles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of commits in projects using this tooling follow conventional commit format (measured via git log analysis)
- **SC-002**: Developers can install commit validation in under 2 minutes (run setup command, verify with test commit)
- **SC-003**: Invalid commit messages are rejected within 1 second with clear error messages
- **SC-004**: Guided commit authoring tool reduces commit message format errors by 80% compared to manual authoring
- **SC-005**: Hook installation succeeds on first attempt across macOS, Linux, and Windows (100% success rate in test matrix)
- **SC-006**: Python-only projects validate commits without any Node.js installation (verified in smoke tests)
- **SC-007**: CI validation catches 100% of invalid commits before merge (no invalid commits in main branch)
- **SC-008**: Developers can customize commit types and scopes in under 5 minutes by editing configuration files
- **SC-009**: Tool startup time (hook execution or CLI launch) is under 500ms on standard hardware
- **SC-010**: Documentation enables developers unfamiliar with conventional commits to create valid commits within 10 minutes

## Dependencies & Assumptions *(optional)*

### Dependencies

- **Git 2.0+**: Required for commit-msg hook support and `--no-verify` flag
- **Python 3.11+**: Required for hook scripts and validation logic (Python-only projects)
- **Node.js 20 LTS + package manager**: Required for validation and authoring tools (Node.js projects)
- **Package manager (uv for Python, pnpm for Node.js)**: Required for dependency management and script execution
- **Existing Git repository**: Hooks require Git repository structure (won't work in bare repos or non-Git projects)

### Assumptions

- **Developers have write access to Git hooks directory**: Hook installation requires writing to this directory (standard for cloned repos)
- **Commit messages are UTF-8 encoded**: Validation logic assumes UTF-8, may fail on legacy encodings
- **Projects use semantic versioning**: Conventional commits map to semver (feat→minor, fix→patch, breaking→major)
- **Single Git remote**: Assumes standard remote for CI validation (multi-remote setups require manual config)
- **English commit messages**: Validation rules and prompts are in English (internationalization not in scope)
- **Linear commit history preference**: Tool encourages atomic, well-described commits rather than squash-and-merge
- **Team alignment on commit format**: Assumes team has agreed to use conventional commits (tool enforces, doesn't persuade)

## Out of Scope *(optional)*

### Explicitly Excluded

- **Automatic commit message generation from code changes**: Tool validates/guides format but doesn't analyze diffs to suggest messages
- **Integration with issue tracking systems**: Won't auto-link commits to JIRA/GitHub issues (can be added later)
- **Commit message translation/internationalization**: English only in v1
- **Visual Studio Code extension**: CLI tools only; IDE integration separate feature
- **Commit signing (GPG) integration**: Security/signing orthogonal to message format
- **Enforcing commit squashing strategies**: Tool agnostic to merge vs rebase vs squash workflows
- **Analyzing commit history quality metrics**: No reports on commit frequency, message quality scores, etc.
- **Pre-commit hooks (linting, testing)**: This feature is commit-msg hook only; pre-commit separate concern
- **Support for alternative VCS (Mercurial, SVN)**: Git-only
- **Offline commit message validation in editor**: Would require IDE plugins (out of scope)

## Technical Constraints *(optional)*

### Performance Constraints

- **Hook execution must complete within 1 second**: Validation cannot significantly delay commit workflow (target <500ms)
- **CLI tool startup must complete within 2 seconds**: Interactive prompts should feel instant
- **Configuration parsing must complete within 100ms**: YAML parsing overhead should be negligible

### Platform Constraints

- **Must work without admin/root privileges**: Hook installation via user-level Git hooks (no system-wide config)
- **Must work in air-gapped environments**: All dependencies bundled or installable via package managers (no runtime internet access)
- **Must support Python 3.11-3.13**: Template baseline; no dependencies on newer Python features
- **Must support Node.js 20 LTS**: When Node.js track enabled; no dependencies on newer features

### Integration Constraints

- **Must integrate with existing Riso workflows**: Hooks run alongside existing Git hooks without conflicts
- **Must work with GitHub Actions workflows**: CI validation via existing quality workflows or dedicated workflow
- **Must not require external services**: No SaaS dependencies for validation (fully local operation)
- **Configuration must be template-compatible**: Configuration files rendered from Copier template with conditional blocks

### Security Constraints

- **Hook scripts must not execute arbitrary code**: Validation logic hardcoded, no eval() or exec()
- **Configuration files must not contain secrets**: All config in plain text (no API keys or tokens)
- **CI validation must run in sandboxed environment**: GitHub Actions runners with no persistent state
