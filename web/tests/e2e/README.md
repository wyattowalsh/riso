# E2E Test Suite Documentation

## Overview

This directory contains comprehensive end-to-end (E2E) tests for the Riso wizard using Playwright. The tests validate the complete user journey through the project configuration wizard.

## Test Files

### `smoke.spec.ts`

Basic smoke tests that verify:

- Homepage loads correctly
- Wizard form is visible and interactive

### `wizard.spec.ts`

Comprehensive wizard functionality tests covering:

#### Wizard Complete Flow

- **complete wizard flow from start to finish**: Tests the entire 6-step wizard journey
- **preset loading populates form and jumps to review**: Validates preset functionality
- **navigation between steps preserves state**: Ensures user input is maintained during navigation
- **sidebar summary updates in real-time**: Verifies live configuration preview
- **step indicator shows progress correctly**: Tests visual progress indicators
- **clicking step indicators allows navigation**: Validates step navigation via indicators

#### Wizard Error Handling

- **shows validation error for invalid project name**: Tests various invalid name patterns
- **accepts valid project names**: Validates correct name formats
- **navigation works even without project name filled**: Tests non-blocking navigation

#### Wizard Responsive Behavior

- **works on mobile viewport**: Tests mobile compatibility (375×667)

#### Wizard Output Generation

- **generates copier output with configuration**: Validates YAML output generation
- **copy to clipboard functionality works**: Tests clipboard API integration

#### Wizard Advanced Features

- **theme switcher works throughout wizard**: Tests dark/light mode toggle
- **progress bar shows current step**: Validates step tracking in sidebar
- **multiple presets can be selected sequentially**: Tests preset switching

## Test Statistics

- **Total Tests**: 17
- **All Passing**: ✅
- **Test Duration**: ~37 seconds
- **Browser**: Chromium (Desktop Chrome)

## Running Tests

### Standard Run

```bash
cd web
pnpm test:e2e
```

### Headed Mode (Visual)

```bash
cd web
pnpm test:e2e --headed
```

### Debug Mode

```bash
cd web
pnpm test:e2e --debug
```

### UI Mode (Interactive)

```bash
cd web
pnpm playwright test --ui
```

### Specific Test File

```bash
cd web
pnpm playwright test wizard.spec.ts
```

### Single Test

```bash
cd web
pnpm playwright test -g "complete wizard flow"
```

## Configuration

Tests are configured in `/web/playwright.config.ts`:

- Base URL: `http://localhost:5173`
- Automatic dev server startup
- Retry on failure: 2 times (CI only)
- HTML reporter for results
- Trace on first retry

## Test Patterns and Best Practices

### Locator Strategy

Tests use semantic selectors prioritizing accessibility:

1. Role-based: `page.getByRole('button', { name: /next/i })`
1. Label-based: `page.getByLabel(/project name/i)`
1. ID-based: `page.locator('#projectName')`
1. Exact text matches for disambiguation

### Common Issues and Solutions

**Strict Mode Violations**: When multiple elements match a selector, use exact matches:

```typescript
// ❌ Ambiguous
page.getByRole('heading', { name: /documentation/i })

// ✅ Specific
page.getByRole('heading', { name: 'Documentation', exact: true })
```

**Timeouts**: Increase timeout for slow operations:

```typescript
await expect(element).toBeVisible({ timeout: 10000 })
```

**State Preservation**: Verify state persists across navigation:

```typescript
const input = await page.locator('#projectName').inputValue()
expect(input).toBe('expected-value')
```

## Test Coverage

### User Flows Covered

- ✅ Linear wizard progression (6 steps)
- ✅ Forward/backward navigation
- ✅ Preset application
- ✅ Form validation
- ✅ Real-time sidebar updates
- ✅ Output generation
- ✅ Theme switching
- ✅ Mobile responsiveness
- ✅ Clipboard operations

### Not Covered (Future Enhancements)

- File upload/download
- External API integration
- Multi-browser testing (Firefox, Safari)
- Performance benchmarks
- Accessibility audit
- Visual regression testing

## Debugging Failed Tests

### View Test Report

```bash
cd web
pnpm playwright show-report
```

### Screenshots and Traces

Failed tests automatically generate:

- Screenshots: `test-results/*/error-context.md`
- Traces: `test-results/*/trace.zip`

### Common Debugging Commands

```bash
# Run with trace
pnpm playwright test --trace on

# Run in debug mode
pnpm playwright test --debug

# Run specific test with headed mode
pnpm playwright test -g "preset loading" --headed
```

## CI/CD Integration

Tests run automatically in GitHub Actions:

- On pull requests
- On main branch commits
- With retry logic for flaky tests
- Generates HTML report artifact

## Maintenance

### When to Update Tests

- UI component changes (button text, labels)
- New wizard steps added
- Validation logic changes
- New features added to wizard

### Test Hygiene

- Keep tests independent
- Use exact selectors when possible
- Add comments for complex logic
- Group related tests in describe blocks
- Clean up test data between runs

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
