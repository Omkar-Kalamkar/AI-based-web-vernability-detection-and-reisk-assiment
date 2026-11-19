import { chromium } from 'playwright'

const browser = await chromium.launch({ channel: 'msedge', headless: true })
const page = await browser.newPage()
page.on('pageerror', (error) => console.log('PAGEERROR:', error.message))
page.on('console', (message) => {
  if (message.type() === 'error') console.log('CONSOLE ERROR:', message.text())
})

const step = async (name, fn) => {
  try {
    await fn()
    console.log('OK', name)
  } catch (error) {
    console.log('FAIL', name, error.message.split('\n')[0])
  }
}

await step('goto login', () => page.goto('http://127.0.0.1:5173/login'))
await step('fill demo', () => page.getByRole('button', { name: /fill demo credentials/i }).click())
await step('sign in', () => page.getByRole('button', { name: /sign in/i }).click())
await step('wait dashboard', () => page.waitForURL('http://127.0.0.1:5173/', { timeout: 10000 }))
console.log('URL after login:', page.url())
console.log('BODY:', (await page.locator('body').innerText()).slice(0, 500))

await step('go scan', () => page.getByRole('link', { name: /new scan/i }).click())
await step('check auth', () => page.getByRole('checkbox').check())
await step('start scan', () => page.getByRole('button', { name: /start secure scan/i }).click())
await page.waitForTimeout(12000)
console.log('SCAN TEXT:', (await page.locator('body').innerText()).slice(0, 1200))

await browser.close()
