# Changelog

All notable changes to the Riso project template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Comprehensive pre-commit stack with security and quality hooks
  - Python: ruff, ty, pylint, vulture
  - Security: gitleaks, pip-audit
  - Shell: shellcheck
  - Docs: codespell, mdformat
  - CI: actionlint, check-jsonschema
- SDLC tooling integration
  - commitlint for commit message validation
  - commitizen for interactive commits
  - semantic-release for automated versioning
  - Release drafter for PR descriptions
  - Auto-labeler for PR categorization
- Profile-aware pre-commit configuration in template
  - Standard profile: Fast, essential hooks
  - Strict profile: Comprehensive validation
- Post-generation hook auto-installs pre-commit hooks
- Makefile targets: hooks, hooks-run, hooks-update, release

### Changed

- Fixed .gitignore CMake section incorrectly ignoring project Makefile

### Documentation

- Added comprehensive pre-commit test suite (30 tests)

---

*This changelog is automatically updated by [semantic-release](https://github.com/semantic-release/semantic-release).*
