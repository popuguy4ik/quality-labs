import { test as base, expect } from '@playwright/test';

// Реклама на сайте открывает всплывающие окна и мешает кликам, поэтому ее блокируем
const ADS = /googlesyndication|doubleclick|googleadservices|adservice|fundingchoices|googletagmanager|google-analytics/;

export const test = base.extend({
  page: async ({ page }, use) => {
    await page.route('**/*', (route) => (ADS.test(route.request().url()) ? route.abort() : route.continue()));
    await use(page);
  },
});
export { expect };
