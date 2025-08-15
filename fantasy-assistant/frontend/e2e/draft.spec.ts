import { test, expect } from '@playwright/test'

test.describe('Draft Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should navigate to draft page', async ({ page }) => {
    await page.click('text=Start Draft')
    await expect(page).toHaveURL('/draft')
    await expect(page.locator('h1')).toContainText('Live Draft Board')
  })

  test('should display draft board tabs', async ({ page }) => {
    await page.goto('/draft')
    
    // Check all tabs are visible
    await expect(page.locator('text=Available')).toBeVisible()
    await expect(page.locator('text=Taken')).toBeVisible()
    await expect(page.locator('text=My Queue')).toBeVisible()
    await expect(page.locator('text=Advice')).toBeVisible()
  })

  test('should switch between tabs', async ({ page }) => {
    await page.goto('/draft')
    
    // Start on available tab
    await expect(page.locator('text=Available Players')).toBeVisible()
    
    // Switch to advice tab
    await page.click('button:has-text("Advice")')
    await expect(page.locator('text=AI Draft Advice')).toBeVisible()
    
    // Switch to queue tab
    await page.click('button:has-text("My Queue")')
    await expect(page.locator('text=My Draft Queue')).toBeVisible()
  })

  test('should show top recommendations', async ({ page }) => {
    await page.goto('/draft')
    
    // Check that recommendations section exists
    await expect(page.locator('text=Top Recommendations')).toBeVisible()
    
    // Should have 3 recommendation cards
    const recommendations = page.locator('[data-testid="recommendation-card"]')
    await expect(recommendations).toHaveCount(3)
  })

  test('should filter available players by position', async ({ page }) => {
    await page.goto('/draft')
    
    // Should start with "All Positions" selected
    await expect(page.locator('select')).toHaveValue('All Positions')
    
    // Change to QB filter
    await page.selectOption('select', 'QB')
    await expect(page.locator('select')).toHaveValue('QB')
  })

  test('should add players to queue', async ({ page }) => {
    await page.goto('/draft')
    
    // Click "Add to Queue" button
    await page.click('button:has-text("Add to Queue"):first')
    
    // Switch to queue tab to verify
    await page.click('button:has-text("My Queue")')
    
    // Should no longer show empty state
    await expect(page.locator('text=Add players to your queue')).not.toBeVisible()
  })

  test('should display draft advice', async ({ page }) => {
    await page.goto('/draft')
    await page.click('button:has-text("Advice")')
    
    // Should show AI recommendation
    await expect(page.locator('text=Recommendation')).toBeVisible()
    
    // Should show strategy suggestions
    await expect(page.locator('text=Strategy: Zero RB')).toBeVisible()
    await expect(page.locator('text=Strategy: Robust RB')).toBeVisible()
  })

  test('should show current pick status', async ({ page }) => {
    await page.goto('/draft')
    
    // Should show round and pick info
    await expect(page.locator('text=Round 1, Pick 1')).toBeVisible()
    await expect(page.locator('text=On the Clock')).toBeVisible()
  })
})