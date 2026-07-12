import { test, expect } from '@playwright/test';

test.describe('Wizard Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Riso/i);
  });

  test('wizard form is visible', async ({ page }) => {
    await page.goto('/');
    // ProjectBasics uses id="projectName" (label association may vary)
    const projectNameInput = page.locator('#projectName');
    await expect(projectNameInput).toBeVisible({ timeout: 15000 });
  });
});
