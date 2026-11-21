# ЛР2. E2E-тесты Playwright

```bash
npm ci
npx playwright install
npx playwright test
DEMO=1 npx playwright test --grep @demo --project=chromium   # падающий тест для разбора trace
```

CI: `.github/workflows/lab2-e2e.yml`
