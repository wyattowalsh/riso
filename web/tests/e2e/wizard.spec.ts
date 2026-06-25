import { test, expect } from '@playwright/test';

const PYTHON_CLI_PRESET = /Python CLI Tool/i;
const PYTHON_API_PRESET = /Python REST API/i;
const REVIEW_HEADING = /Review.*Generate/i;

test.describe('Wizard Complete Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('complete wizard flow from start to finish', async ({ page }) => {
    const projectNameInput = page.locator('#projectName');
    await expect(projectNameInput).toBeVisible();
    await projectNameInput.fill('my-test-project');

    await page.getByRole('button', { name: 'Single Package One package, simpler structure for focused projects' }).click();
    await page.getByRole('button', { name: 'Standard Balanced linting, 80% coverage target, recommended for most projects' }).click();
    await page.getByRole('button', { name: /^next$/i }).click();

    await expect(page.getByRole('heading', { name: /components/i })).toBeVisible();
    await page.getByRole('button', { name: /^next$/i }).click();

    await expect(page.getByRole('heading', { name: 'Documentation', exact: true })).toBeVisible();
    await page.getByRole('button', { name: /^next$/i }).click();

    await expect(page.getByRole('heading', { name: /saas/i })).toBeVisible();
    await page.getByRole('button', { name: /^next$/i }).click();

    await expect(page.getByRole('heading', { name: 'AI Tools', exact: true })).toBeVisible();
    await page.getByRole('button', { name: 'Generate', exact: true }).click();

    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 10000 });
  });

  test('preset loading populates form and jumps to review', async ({ page }) => {
    const pythonCliPreset = page.getByRole('button', { name: PYTHON_CLI_PRESET });
    await expect(pythonCliPreset).toBeVisible();
    await pythonCliPreset.click();

    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('CLI (python)', { exact: true })).toBeVisible({ timeout: 5000 });
  });

  test('navigation between steps preserves state', async ({ page }) => {
    const projectNameInput = page.locator('#projectName');
    await projectNameInput.fill('test-project');

    const monorepoButton = page.getByRole('button', { name: 'Monorepo Multiple packages sharing tooling, ideal for polyglot stacks' });
    await monorepoButton.click();

    await page.getByRole('button', { name: /^next$/i }).click();
    await expect(page.getByRole('heading', { name: /components/i })).toBeVisible();

    await page.getByRole('button', { name: /previous/i }).click();

    await expect(projectNameInput).toBeVisible();
    expect(await projectNameInput.inputValue()).toBe('test-project');
    await expect(monorepoButton).toHaveClass(/border-riso-federal-blue|bg-gradient/);
  });

  test('wizard form state updates in real-time', async ({ page }) => {
    const projectNameInput = page.locator('#projectName');
    await projectNameInput.fill('realtime-test');
    await expect(projectNameInput).toHaveValue('realtime-test');

    const monorepoButton = page.getByRole('button', { name: 'Monorepo Multiple packages sharing tooling, ideal for polyglot stacks' });
    await monorepoButton.click();
    await expect(monorepoButton).toHaveClass(/border-riso-federal-blue|bg-gradient/);
  });

  test('step indicator shows progress correctly', async ({ page }) => {
    const stepIndicators = page.locator('.step-indicator, [aria-label*="Go to step"]');
    await expect(stepIndicators.first()).toBeVisible();

    const firstStep = page.locator('.step-indicator.active, button[aria-current="step"]').first();
    await expect(firstStep).toBeVisible();

    await page.locator('#projectName').fill('progress-test');
    await page.getByRole('button', { name: /^next$/i }).click();
    await page.waitForTimeout(500);

    const completedStep = page.locator('.step-indicator.completed').first();
    await expect(completedStep).toBeVisible();
  });

  test('clicking step indicators allows navigation to completed steps', async ({ page }) => {
    await page.locator('#projectName').fill('nav-test');
    await page.getByRole('button', { name: /^next$/i }).click();

    const stepIndicators = page.locator('button[aria-label="Go to step 1"]');
    if (await stepIndicators.first().isVisible()) {
      await stepIndicators.first().click();
      await expect(page.locator('#projectName')).toBeVisible();
      expect(await page.locator('#projectName').inputValue()).toBe('nav-test');
    }
  });
});

test.describe('Wizard Error Handling', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('shows validation error for invalid project name', async ({ page }) => {
    const projectNameInput = page.locator('#projectName');

    const invalidNames = [
      'Invalid Name With Spaces',
      '123-starts-with-number',
      'has!special@chars',
      'a',
    ];

    for (const invalidName of invalidNames) {
      await projectNameInput.fill(invalidName);
      const errorMessage = page.locator('text=/must start with a letter|contain only|at least 2 characters/i');
      await expect(errorMessage).toBeVisible({ timeout: 2000 });
      await projectNameInput.clear();
    }
  });

  test('accepts valid project names', async ({ page }) => {
    const projectNameInput = page.locator('#projectName');

    const validNames = ['my-project', 'my_project', 'MyProject', 'project123', 'a1'];

    for (const validName of validNames) {
      await projectNameInput.fill(validName);
      const errorMessage = page.locator('text=/must start with a letter|contain only/i');
      await expect(errorMessage).not.toBeVisible();
      await projectNameInput.clear();
    }
  });

  test('navigation works even without project name filled', async ({ page }) => {
    await page.getByRole('button', { name: /^next$/i }).click();
    await expect(page.getByRole('heading', { name: /components/i })).toBeVisible();
  });
});

test.describe('Wizard Responsive Behavior', () => {
  test('works on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    await expect(page.locator('#projectName')).toBeVisible();
    await page.locator('#projectName').fill('mobile-test');
    await page.getByRole('button', { name: /^next$/i }).click();
    await expect(page.getByRole('heading', { name: /components/i })).toBeVisible();
  });
});

test.describe('Wizard Output Generation', () => {
  test('generates copier output with configuration', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: PYTHON_CLI_PRESET }).click();
    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 5000 });

    const outputSection = page.locator('pre, code, .output, [class*="yaml"]');
    await expect(outputSection.first()).toBeVisible();

    const content = page.locator('text=/project_name|project_layout|quality_profile/i');
    await expect(content.first()).toBeVisible();
  });

  test('copy to clipboard functionality works', async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.goto('/');

    await page.getByRole('button', { name: PYTHON_CLI_PRESET }).click();
    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 5000 });

    const copyButton = page.getByRole('button', { name: /copy/i });
    if (await copyButton.isVisible()) {
      await copyButton.click();
      await expect(page.getByText(/copied|success/i)).toBeVisible({ timeout: 2000 });
    }
  });
});

test.describe('Wizard Advanced Features', () => {
  test('theme switcher works throughout wizard', async ({ page }) => {
    await page.goto('/');

    const themeToggle = page.getByRole('button', { name: /^switch to (dark|light) mode$/i });
    const html = page.locator('html');
    const initialClass = await html.getAttribute('class');

    await themeToggle.click();
    await page.waitForTimeout(300);

    const newClass = await html.getAttribute('class');
    expect(newClass).not.toBe(initialClass);
  });

  test('progress bar shows current step', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('button[aria-current="step"]')).toContainText('Project');

    await page.locator('#projectName').fill('progress-test');
    await page.getByRole('button', { name: /^next$/i }).click();
    await page.waitForTimeout(500);

    await expect(page.locator('button[aria-current="step"]')).toContainText('Modules');
  });

  test('multiple presets can be selected sequentially', async ({ page }) => {
    await page.goto('/');

    await page.getByRole('button', { name: PYTHON_CLI_PRESET }).click();
    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 5000 });

    await page.goto('/');

    await page.getByRole('button', { name: PYTHON_API_PRESET }).click();
    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('API (python)', { exact: true })).toBeVisible({ timeout: 5000 });
  });
});
