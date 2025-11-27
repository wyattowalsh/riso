## Description

<!-- Provide a clear and concise description of your changes -->

## Related Issues

<!-- Link to related issues using "Fixes #123" or "Relates to #123" -->

Fixes #

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test addition/modification
- [ ] CI/CD change
- [ ] Dependency update

## Component

<!-- Check all components affected by this PR -->

- [ ] Template system (copier.yml, hooks)
- [ ] CLI module
- [ ] API module (Python/FastAPI)
- [ ] API module (Node/Fastify)
- [ ] GraphQL module
- [ ] MCP module
- [ ] WebSocket module
- [ ] Documentation site templates
- [ ] SaaS starter
- [ ] Quality tools
- [ ] CI/CD workflows
- [ ] Scripts/automation
- [ ] Tests
- [ ] Documentation

## Changes Made

<!-- Provide a detailed list of changes -->

-
-
-

## Testing Performed

<!-- Describe the testing you've done -->

### Manual Testing

- [ ] Rendered template with default options
- [ ] Rendered template with affected modules enabled
- [ ] Tested all affected features manually
- [ ] Verified generated code compiles/runs
- [ ] Checked generated documentation builds

### Automated Testing

- [ ] All existing tests pass
- [ ] Added new tests for new features
- [ ] Updated tests for modified features
- [ ] Tests cover edge cases
- [ ] Coverage maintained or improved

### Quality Checks

- [ ] `make quality` or `uv run task quality` passes
- [ ] `ruff format` applied
- [ ] `mypy` type checking passes
- [ ] Pre-commit hooks pass
- [ ] No security issues from `bandit`

## Screenshots/Examples

<!-- If applicable, add screenshots or example output -->

<details>
<summary>Click to expand</summary>

```
<!-- Paste example output, configuration, or screenshots here -->
```

</details>

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

- [ ] This PR introduces breaking changes
- [ ] Migration guide included
- [ ] CHANGELOG.md updated

**Impact:**

**Migration:**

## Checklist

<!-- Verify you've completed all required items -->

### Code Quality

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No unnecessary console.log or print statements
- [ ] No commented-out code (unless explained)
- [ ] Error handling is appropriate
- [ ] No hardcoded values (use config/env vars)

### Documentation

- [ ] Updated README.md (if applicable)
- [ ] Updated AGENTS.md (if workflow changes)
- [ ] Updated relevant docs in `docs/` directory
- [ ] Added/updated docstrings for new functions
- [ ] Added/updated comments for complex code
- [ ] Updated CHANGELOG.md

### Dependencies

- [ ] No new dependencies added
- [ ] OR: New dependencies documented and justified
- [ ] Dependency versions pinned appropriately
- [ ] `pyproject.toml` or `package.json` updated

### Git

- [ ] Commit messages follow conventional commits format
- [ ] Commits are logical and atomic
- [ ] No merge conflicts with main branch
- [ ] Branch is up to date with main

### Testing

- [ ] Existing tests pass locally
- [ ] New tests added for new features
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Integration tests pass (if applicable)

### Security

- [ ] No secrets or credentials committed
- [ ] No security vulnerabilities introduced
- [ ] Input validation added where needed
- [ ] SQL injection protection (if applicable)
- [ ] XSS protection (if applicable)

### Review

- [ ] Ready for review
- [ ] Reviewers assigned
- [ ] Labels added
- [ ] Milestone set (if applicable)

## Additional Notes

<!-- Add any additional notes for reviewers -->

## Reviewer Checklist

<!-- For reviewers to complete -->

- [ ] Code review completed
- [ ] Tests verified
- [ ] Documentation verified
- [ ] No security concerns
- [ ] Approved

---

<!--
Thank you for your contribution! 🎉
Please ensure all checkboxes are marked before requesting review.
-->
