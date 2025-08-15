import { test, expect } from '@playwright/test';

test('draft flow', async ({ page }) => {
  await page.goto('/draft');
  await expect(page).toHaveText('Draft Board');
});
