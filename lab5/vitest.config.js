import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      include: ['src/**/*.js'],
      exclude: ['src/**/*.test.js'],
      reporter: ['text', 'html', 'lcov', 'json-summary'],
      thresholds: { lines: 80, branches: 80 },
    },
  },
});
