# Breaking Changes

This document tracks breaking changes in RISO by version. Review this document before upgrading to understand what may require updates in your generated projects.

## [Unreleased]

### Template Changes
- None yet

### API Changes
- None yet

### Configuration Changes
- None yet

### Hook Changes
- None yet

---

## Versioning Policy

RISO follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Breaking changes to generated project structure or configuration
- **MINOR** version: New features that don't break existing generated projects
- **PATCH** version: Bug fixes and documentation updates

### What Constitutes a Breaking Change

1. **Template Structure Changes**
   - Removing or renaming files that may already exist in generated projects
   - Changing directory structure
   - Modifying file naming conventions

2. **Configuration Changes**
   - Removing or renaming copier.yml variables
   - Changing default values that affect behavior
   - Modifying dependency requirements

3. **Hook Changes**
   - Changing hook behavior that affects generation
   - Modifying tool requirements
   - Altering validation rules

### Migration Guides

When breaking changes occur, migration guides will be provided here to help you update your existing generated projects.

---

## Reporting Issues

If you encounter issues after upgrading, please:

1. Check this document for known breaking changes
2. Review the [CHANGELOG.md](CHANGELOG.md) for related updates
3. Open an issue on GitHub with:
   - Your previous RISO version
   - Your current RISO version
   - Description of the issue
   - Steps to reproduce
