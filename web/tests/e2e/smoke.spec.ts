import { test, expect } from '@playwright/test';

test.describe('Wizard Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Riso/i);
  });

  test('wizard form is visible', async ({ page }) => {
    await page.goto('/');
    // Check for project name input or wizard step indicator
    const projectNameInput = page.getByLabel(/project name/i);
    await expect(projectNameInput).toBeVisible();
  });
});
