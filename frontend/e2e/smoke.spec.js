import { expect, test } from '@playwright/test'

test('end-to-end login, scan, findings, reports and navigation', async ({ page }) => {
  const errors = []
  page.on('pageerror', (error) => errors.push(error.message))

  await page.goto('/login')
  await page.getByRole('button', { name: /fill demo credentials/i }).click()
  await page.getByRole('button', { name: /sign in/i }).click()
  await expect(page).toHaveURL('http://127.0.0.1:5173/')
  await expect(page.getByText(/welcome back/i)).toBeVisible()

  await page.getByRole('link', { name: /new scan/i }).click()
  await expect(page.getByText(/configure a security scan/i)).toBeVisible()
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: /start secure scan/i }).click()

  await expect(page.getByText(/completed/i).first()).toBeVisible({ timeout: 45000 })
  await expect(page.getByText(/detected findings/i)).toBeVisible()
  const findingButton = page.locator('button').filter({ hasText: 'Unencrypted HTTP transport' }).first()
  await expect(findingButton).toBeVisible()
  await findingButton.click()
  await expect(page.getByText(/in simple terms/i)).toBeVisible()
  await page.getByRole('button', { name: 'Close dialog' }).click()

  const downloadEvent = page.waitForEvent('download')
  await page.getByRole('button', { name: /pdf report/i }).click()
  const download = await downloadEvent
  expect(download.suggestedFilename()).toContain('.pdf')

  for (const [link, heading] of [
    [/vulnerabilities/i, /review and manage all detected findings/i],
    [/ai risk assessment/i, /transparent scoring/i],
    [/reports/i, /download pdf and csv/i],
    [/scan history/i, /compare results/i],
    [/settings/i, /workspace preferences/i],
  ]) {
    await page.getByRole('link', { name: link }).first().click()
    await expect(page.getByText(heading).first()).toBeVisible()
  }

  await page.getByRole('button', { name: /logout/i }).first().click()
  await expect(page).toHaveURL('http://127.0.0.1:5173/login')
  expect(errors).toEqual([])
})
