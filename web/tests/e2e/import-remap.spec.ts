import path from 'node:path'
import { test, expect } from '@playwright/test'

const REVIEW_HEADING = /Review.*Generate/i
const FIXTURE_DIR = path.join(process.cwd(), 'tests/e2e/fixtures/remap')

test.describe('WEB-T06 YAML import remap', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.clear()
    })
    await page.reload()
    await expect(page.locator('#projectName')).toBeVisible()
  })

  test('imports remapped 1.x YAML and applies canonical dests', async ({
    page,
  }) => {
    const input = page.getByTestId('preset-import-input')
    await input.setInputFiles(path.join(FIXTURE_DIR, 'mixed.yml'))

    await expect(page.getByTestId('preset-import-preview')).toBeVisible()
    await expect(page.getByTestId('preset-import-preview')).toContainText(
      'api_tracks',
    )
    const applyButton = page.getByTestId('custom-preset-apply-remap-mixed')
    await expect(applyButton).toBeVisible()
    await applyButton.click({ force: true })
    await expect(page.getByRole('heading', { name: REVIEW_HEADING })).toBeVisible({
      timeout: 10_000,
    })
    await expect(page.getByText('API (python, go)', { exact: true })).toBeVisible()

    await page.getByRole('tab', { name: /CLI Command/i }).click()
    await page.getByRole('button', { name: /YAML Config/i }).click()
    const yaml = await page
      .locator('#review-tab-panel-cli-command pre code')
      .first()
      .innerText()
    expect(yaml).toContain('api_module:')
    expect(yaml).toContain('api_languages:')
    expect(yaml).toContain('docs_framework:')
    expect(yaml).toContain('saas_infra_module:')
    expect(yaml).toContain('saas_auth_module:')
    expect(yaml).toContain('saas_billing_module:')
    expect(yaml).toContain('saas_admin_dashboard:')
    expect(yaml).toContain('openspec_extra:')
    expect(yaml).not.toMatch(/(?:^|\n)api_tracks:/)
    expect(yaml).not.toMatch(/(?:^|\n)mcp_language:/)
    expect(yaml).not.toMatch(/(?:^|\n)docs_site:/)
    expect(yaml).not.toMatch(/(?:^|\n)saas_auth:/)
    expect(yaml).not.toMatch(/(?:^|\n)saas_billing:/)
    expect(yaml).not.toMatch(/(?:^|\n)saas_starter_module:/)
    expect(yaml).not.toMatch(/(?:^|\n)include_admin:/)
  })

  test('shows leftover error for unmapped removed keys', async ({ page }) => {
    const input = page.getByTestId('preset-import-input')
    await input.setInputFiles(path.join(FIXTURE_DIR, 'leftover.yml'))

    const error = page.getByTestId('preset-import-error')
    await expect(error).toBeVisible()
    await expect(error).toContainText('saas_auth')
    await expect(error).toContainText('saas_auth_module')
    await expect(page.getByTestId('preset-import-preview')).toHaveCount(0)
    await expect(
      page.getByRole('button', { name: /remap-leftover/i }),
    ).toHaveCount(0)
  })
})
