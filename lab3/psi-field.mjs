import { launch, newPage, emulate, sleep } from '/Users/immat0x1/Documents/lab2_webdesign/_work/tools/cdp.mjs';
import fs from 'node:fs';
const [, , site, tag] = process.argv;
const browser = await launch({ args: ['--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'] });
try {
  const page = await newPage(browser);
  await emulate(page, { width: 1280, height: 1500, mobile: false });
  await page.s('Page.navigate', { url: `https://pagespeed.web.dev/analysis?url=${encodeURIComponent(site)}&form_factor=mobile&hl=ru` });
  for (let i = 0; i < 90; i++) { await sleep(2000); if (await page.evaluate(`[...document.querySelectorAll('.lh-gauge__percentage')].filter(e => e.offsetParent && e.textContent.trim()).length >= 4`).catch(() => false)) break; }
  await sleep(3000);
  const t = await page.evaluate('document.body.innerText');
  fs.writeFileSync(`psi/${tag}.txt`, t);
  await page.evaluate('scrollTo(0, 0)');
  const { data } = await page.s('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`shots/psi-${tag}.png`, Buffer.from(data, 'base64'));
} finally { await browser.close(); }
