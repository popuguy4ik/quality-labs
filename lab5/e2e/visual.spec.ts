import { test, expect } from '@playwright/test';

// Визуальная регрессия: сравнение с эталонными скриншотами (только Chromium)
test.describe('Визуальные тесты', () => {
  test.use({ viewport: { width: 1280, height: 800 } });

  for (const [name, path] of [['home', '/'], ['features', '/features.html'], ['contacts', '/contacts.html']]) {
    test(`первый экран: ${name}`, async ({ page }) => {
      await page.emulateMedia({ colorScheme: 'light', reducedMotion: 'reduce' });
      await page.route('**/openstreetmap.org/**', (r) => r.abort());
      await page.goto(path);
      await page.evaluate(() => document.fonts.ready);
      await expect(page).toHaveScreenshot(`${name}.png`);
    });
  }
});
