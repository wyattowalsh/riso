---
title: Python Testing Audit Prompt for Claude Code
date: 2026-01-07
status: active
category: audit-prompts
---

# Python Testing Audit Prompt for Claude Code

> **Usage:** Copy this entire prompt into Claude Code to conduct a comprehensive audit of Python testing logic using parallel subagents.

______________________________________________________________________

## PROMPT START

You are conducting a deep, targeted, robust audit of all Python testing-related logic in this codebase. Execute this audit using iterative batches of massively parallel subagents for maximum efficiency.

### Execution Strategy

```
PHASE 1: Discovery & Inventory (8 parallel agents)
PHASE 2: Test Quality Deep-Dive (10 parallel agents)
PHASE 3: Coverage & Gap Analysis (6 parallel agents)
PHASE 4: Configuration & Infrastructure (6 parallel agents)
PHASE 5: Synthesis & Recommendations (4 parallel agents)
```

**Total: 34 agents across 5 phases**

______________________________________________________________________

## PHASE 1: Discovery & Inventory

Launch 8 parallel agents to map the testing landscape:

### Agent 1.1: Test File Inventory

```
Prompt: "Inventory ALL test files in this codebase. For each file report:
- Full path
- Number of test functions (count functions starting with test_)
- Number of test classes (count classes starting with Test)
- Approximate line count
- Primary module/feature being tested

Output as a markdown table sorted by line count descending.
Search patterns: **/test_*.py, **/*_test.py, tests/**/*.py"
```

### Agent 1.2: Pytest Configuration Analysis

```
Prompt: "Analyze ALL pytest configuration in this codebase:
- pyproject.toml [tool.pytest.ini_options] section
- pytest.ini if exists
- conftest.py files (list all, note their scope)
- setup.cfg pytest section if exists

For each config, document:
- Configured test paths
- Markers defined
- Plugins enabled
- Custom options
- Potential conflicts or redundancies"
```

### Agent 1.3: Test Fixture Inventory

```
Prompt: "Inventory ALL pytest fixtures in this codebase:
- Location (which conftest.py or test file)
- Fixture name
- Scope (function/class/module/session)
- Whether it's autouse
- Dependencies (other fixtures it uses)
- Brief description of what it provides

Focus on conftest.py files first, then inline fixtures.
Flag any fixtures that appear duplicated or could be consolidated."
```

### Agent 1.4: Mock & Patch Pattern Catalog

```
Prompt: "Catalog ALL mocking patterns used in tests:
- unittest.mock usage (patch, MagicMock, Mock, PropertyMock)
- pytest-mock usage (mocker fixture)
- monkeypatch usage patterns
- Any custom mock utilities

For each pattern found, note:
- File location
- What's being mocked
- Whether it's a decorator, context manager, or fixture
- Potential issues (over-mocking, implementation coupling)"
```

### Agent 1.5: Test Markers & Categories

```
Prompt: "Analyze test categorization and markers:
- All @pytest.mark.X decorators used
- Custom markers defined in pytest config
- Skip/xfail patterns and their reasons
- Parametrize usage patterns
- Any conditional test execution logic

Create a taxonomy of how tests are organized/categorized.
Identify inconsistencies in marker usage."
```

### Agent 1.6: Assertion Pattern Analysis

```
Prompt: "Analyze assertion patterns across all test files:
- Plain assert usage vs pytest assertions
- Custom assertion helpers
- pytest.raises usage patterns
- pytest.warns usage
- Approximate/tolerance assertions (pytest.approx)
- Collection assertions

Identify:
- Weak assertions (assert True, assert x)
- Missing assertions in tests
- Overly complex assertion chains
- Inconsistent assertion styles"
```

### Agent 1.7: Test Data & Fixtures Files

```
Prompt: "Inventory all test data and fixture files:
- JSON fixtures in tests/
- YAML fixtures
- Sample files for testing
- Factory patterns (factory_boy, or custom)
- Builder patterns for test data

For each, document:
- Location and purpose
- Whether it's realistic/representative
- Potential for data-driven testing expansion
- Staleness risks"
```

### Agent 1.8: Test Dependencies Analysis

```
Prompt: "Analyze test-specific dependencies:
- Test dependencies in pyproject.toml
- pytest plugins installed
- Coverage tools configured
- Any test utilities or helpers

Evaluate:
- Version currency of test dependencies
- Missing useful plugins
- Redundant dependencies
- Security advisories on test deps"
```

______________________________________________________________________

## PHASE 2: Test Quality Deep-Dive

Launch 10 parallel agents for detailed quality analysis:

### Agent 2.1: Unit Test Isolation Audit

```
Prompt: "Audit unit tests for proper isolation:
- Tests that modify global state
- Tests that depend on execution order
- Tests sharing mutable fixtures incorrectly
- Tests with file system side effects not cleaned up
- Tests with network calls not mocked
- os.chdir() or directory changes without restoration

For each violation, provide:
- File:line location
- Nature of the isolation breach
- Recommended fix"
```

### Agent 2.2: Test Naming Convention Audit

```
Prompt: "Audit test naming conventions:
- Test function naming patterns (test_X_should_Y, test_X_when_Y, etc.)
- Test class naming patterns
- Consistency across the codebase
- Descriptiveness of test names
- Tests with ambiguous names

Create a style guide recommendation based on current patterns."
```

### Agent 2.3: Arrange-Act-Assert Pattern Audit

```
Prompt: "Audit tests for clean AAA (Arrange-Act-Assert) structure:
- Tests with clear separation of setup/execution/verification
- Tests with tangled logic
- Tests doing too much (multiple acts)
- Tests with missing assertions
- Tests with setup in assertion phase

Provide examples of good and problematic patterns found."
```

### Agent 2.4: Edge Case Coverage Audit

```
Prompt: "Audit edge case coverage in tests:
- Empty input handling tests
- Null/None handling tests
- Boundary condition tests
- Error condition tests
- Large input tests
- Unicode/encoding tests
- Concurrent access tests (if applicable)

Identify modules with weak edge case coverage."
```

### Agent 2.5: Error Path Testing Audit

```
Prompt: "Audit error handling test coverage:
- Exception raising tests (pytest.raises)
- Error message content verification
- Exception chaining tests
- Cleanup on error tests
- Graceful degradation tests

For each module, assess:
- Are all documented exceptions tested?
- Are error messages verified, not just exception types?
- Are recovery paths tested?"
```

### Agent 2.6: Test Documentation Audit

```
Prompt: "Audit test documentation:
- Docstrings on test functions
- Docstrings on test classes
- Comments explaining complex test logic
- README files in test directories
- Test plan documentation

Assess:
- Coverage of 'why' not just 'what'
- Clarity for new contributors
- Staleness of documentation"
```

### Agent 2.7: Parametrized Test Quality

```
Prompt: "Deep-dive into parametrized tests:
- @pytest.mark.parametrize usage
- Quality of parameter names (ids)
- Coverage of parameter space
- Redundant parameter combinations
- Missing important combinations
- Readability of parametrized tests

Suggest improvements for existing parametrized tests."
```

### Agent 2.8: Integration Test Analysis

```
Prompt: "Analyze integration tests specifically:
- Identification of integration vs unit tests
- Integration test isolation strategies
- External dependency handling
- Database/filesystem integration patterns
- Cleanup strategies
- Test environment requirements

Flag integration tests masquerading as unit tests."
```

### Agent 2.9: Test Performance Analysis

```
Prompt: "Analyze test performance characteristics:
- Slow tests (look for sleep(), large loops, heavy I/O)
- Tests that could be parallelized
- Fixture setup overhead
- Tests with redundant setup
- Opportunities for session-scoped fixtures

Identify the likely slowest tests and optimization opportunities."
```

### Agent 2.10: Flaky Test Detection

```
Prompt: "Identify potential flaky tests:
- Time-dependent tests
- Order-dependent tests
- Tests with race conditions
- Tests depending on external services
- Tests with random elements without seeds
- Tests with floating-point comparisons without tolerance

For each potential flaky test, explain the risk and mitigation."
```

______________________________________________________________________

## PHASE 3: Coverage & Gap Analysis

Launch 6 parallel agents:

### Agent 3.1: Coverage Configuration Audit

```
Prompt: "Audit code coverage configuration:
- Coverage.py configuration in pyproject.toml
- Coverage exclusion patterns
- Branch coverage settings
- Coverage reporting formats
- CI coverage integration

Identify:
- Over-broad exclusions hiding untested code
- Missing coverage for important paths
- Coverage threshold configuration"
```

### Agent 3.2: Untested Code Identification

```
Prompt: "Identify likely untested code paths:
- Public functions/methods without corresponding tests
- Error handlers that appear untested
- Conditional branches that seem uncovered
- Recently added code without tests
- Complex functions with simple tests

Cross-reference test files with source files to find gaps."
```

### Agent 3.3: Test-to-Code Ratio Analysis

```
Prompt: "Analyze test-to-code ratios:
- Lines of test code vs lines of production code per module
- Test function count vs production function count
- Identify modules with disproportionately low test coverage

Create a heatmap-style report of testing density."
```

### Agent 3.4: Critical Path Coverage

```
Prompt: "Assess test coverage of critical paths:
- Main entry points (CLI, API endpoints)
- Core business logic
- Security-sensitive code
- Data validation code
- Error recovery paths

Prioritize gaps by criticality of the untested code."
```

### Agent 3.5: Regression Test Assessment

```
Prompt: "Assess regression testing capability:
- Tests that would catch common regression types
- Tests covering previously fixed bugs
- Tests for documented edge cases
- Tests for integration points

Identify areas where regressions could slip through."
```

### Agent 3.6: API Contract Testing

```
Prompt: "Analyze API/contract testing:
- Public API surface test coverage
- Return type verification
- Input validation testing
- Backward compatibility tests
- Deprecation warning tests

Assess whether public interfaces are adequately tested."
```

______________________________________________________________________

## PHASE 4: Configuration & Infrastructure

Launch 6 parallel agents:

### Agent 4.1: CI Test Integration Audit

```
Prompt: "Audit CI/CD test integration:
- GitHub Actions test workflows
- Test matrix configuration
- Parallel test execution setup
- Test artifact handling
- Failure notification configuration

Identify:
- Missing Python version coverage
- Suboptimal parallelization
- Missing OS coverage if relevant"
```

### Agent 4.2: Test Environment Management

```
Prompt: "Audit test environment management:
- Virtual environment handling in tests
- Environment variable management
- Test database/service setup
- Docker usage for tests
- Cleanup procedures

Flag environment leakage risks."
```

### Agent 4.3: Test Utility Code Quality

```
Prompt: "Audit test utility/helper code:
- Custom test utilities in conftest.py
- Test helper modules
- Shared test constants
- Test base classes

Assess:
- Code quality of test utilities
- Reusability
- Documentation
- Potential for pytest plugins"
```

### Agent 4.4: Pytest Plugin Utilization

```
Prompt: "Analyze pytest plugin utilization:
- Currently used plugins and their effectiveness
- Plugins that could improve testing
- Custom plugin opportunities
- Plugin configuration optimization

Recommend plugin additions or removals."
```

### Agent 4.5: Test Output & Reporting

```
Prompt: "Audit test output and reporting:
- Console output configuration
- JUnit XML generation
- Coverage report generation
- Custom reporting
- Log capture configuration

Assess readability and CI integration of test reports."
```

### Agent 4.6: Test Maintenance Burden

```
Prompt: "Assess test maintenance burden:
- Tests tightly coupled to implementation
- Tests that break on refactoring
- Overly specific assertions
- Tests testing private methods
- Tests with excessive mocking

Identify tests that are maintenance liabilities."
```

______________________________________________________________________

## PHASE 5: Synthesis & Recommendations

Launch 4 parallel agents:

### Agent 5.1: Critical Issues Synthesis

```
Prompt: "Synthesize critical testing issues from all previous findings:
- P0: Issues that could cause false confidence (tests that don't test)
- P1: Issues that could miss bugs (coverage gaps in critical code)
- P2: Issues affecting test reliability (flaky tests)
- P3: Issues affecting maintainability

Create a prioritized action plan with effort estimates."
```

### Agent 5.2: Quick Wins Identification

```
Prompt: "Identify quick wins for test improvement:
- Low-effort, high-impact improvements
- Simple fixes for common issues
- Configuration changes with big benefits
- Easy coverage additions

Create a checklist of improvements achievable in <1 hour each."
```

### Agent 5.3: Test Architecture Recommendations

```
Prompt: "Provide test architecture recommendations:
- Optimal test directory structure
- Fixture organization strategy
- Test categorization scheme
- Coverage requirements by module type
- Integration test isolation strategy

Create an ideal state architecture document."
```

### Agent 5.4: Testing Standards Document

```
Prompt: "Draft a testing standards document based on findings:
- Naming conventions
- Required test patterns
- Forbidden anti-patterns
- Coverage requirements
- Documentation requirements
- Review checklist for test PRs

Make it actionable and enforceable."
```

______________________________________________________________________

## Output Requirements

After all phases complete, synthesize into:

### 1. Executive Summary

- Total tests: X
- Estimated coverage: X%
- Critical issues: X
- Quick wins: X
- Recommended priority actions

### 2. Issues Table

| ID  | Severity | Category | Description | File(s) | Effort | Impact |
| --- | -------- | -------- | ----------- | ------- | ------ | ------ |

### 3. Metrics Dashboard

- Tests by type (unit/integration/e2e)
- Tests by module
- Fixture count and reuse rate
- Mock density
- Parametrization usage

### 4. Action Plan

Prioritized list of improvements with:

- Description
- Files affected
- Estimated effort
- Expected impact
- Dependencies

______________________________________________________________________

## Execution Instructions

1. **Start Phase 1** - Launch all 8 agents in parallel
1. **Wait for Phase 1** - Collect all outputs
1. **Start Phase 2** - Launch all 10 agents in parallel
1. **Continue sequentially** through phases 3-5
1. **Synthesize** - Combine all findings into final report

Use TodoWrite to track progress through phases.

**BEGIN AUDIT NOW**

______________________________________________________________________

## PROMPT END
