import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  // Падающий тест для задания 3 запускается отдельно: DEMO=1 npx playwright test --grep @demo
  grepInvert: process.env.DEMO ? undefined : /@demo/,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  // Публичный стенд иногда отвечает «heavy load (queue full)»: даем тесту еще две попытки
  retries: 2,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: 'https://automationexercise.com',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    locale: 'ru-RU',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
});
