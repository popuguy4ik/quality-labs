import { test, expect } from '@playwright/test';

test.describe('Сайт «Сова»', () => {
  test('главная: навигация и активный пункт меню', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { level: 1 })).toContainText('хранить секреты');
    await page.getByRole('navigation', { name: 'Основная навигация' }).getByRole('link', { name: 'Возможности' }).click();
    await expect(page).toHaveURL(/features/);
    await expect(page.getByRole('link', { name: 'Возможности', exact: true }).first()).toHaveAttribute('aria-current', 'page');
  });

  test('темная тема сохраняется после перезагрузки', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/');
    const toggle = page.locator('[data-theme-toggle]');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    await toggle.click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  });

  test('мобильное меню открывается и закрывается по Esc', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('/blog.html');
    const burger = page.getByRole('button', { name: 'Открыть меню' });
    await burger.click();
    await expect(burger).toHaveAttribute('aria-expanded', 'true');
    await expect(page.getByRole('dialog', { name: 'Меню' })).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(burger).toHaveAttribute('aria-expanded', 'false');
    await expect(burger).toBeFocused();
  });

  test('форма контактов: ошибки и успешная отправка', async ({ page }) => {
    await page.goto('/contacts.html');
    const form = page.locator('.contact-form');
    await form.getByRole('button', { name: 'Отправить' }).click();
    await expect(page.locator('#name-error')).toHaveText('Заполните это поле');
    await expect(page.locator('#agree-error')).toContainText('согласие');
    await expect(page.locator('#name')).toBeFocused();

    await page.getByLabel('Имя').fill('Илья');
    await page.getByLabel('Почта').fill('ilya@mail.ru');
    await page.getByLabel('Сообщение').fill('Не приходит код входа');
    await page.getByLabel(/Согласен/).check();
    await form.getByRole('button', { name: 'Отправить' }).click();
    await expect(form.getByRole('status')).toContainText('Сообщение отправлено');
  });

  test('блог: пагинация и хлебные крошки', async ({ page }) => {
    await page.goto('/blog.html');
    await expect(page.locator('main .card')).toHaveCount(6);
    await page.getByRole('link', { name: 'Страница 2' }).click();
    await expect(page.locator('main .card')).toHaveCount(3);
    await expect(page.getByRole('navigation', { name: 'Хлебные крошки' })).toContainText('Страница 2');
    await page.getByRole('navigation', { name: 'Хлебные крошки' }).getByRole('link', { name: 'Блог' }).click();
    await expect(page).toHaveURL(/blog$|blog\.html$/);
  });

  test('карточка возможности ведет на детальную страницу', async ({ page }) => {
    await page.goto('/features.html');
    await page.getByRole('link', { name: 'Веб-версия' }).first().click();
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Веб-версия: Сова в любом браузере');
    await expect(page.getByRole('navigation', { name: 'Хлебные крошки' })).toContainText('Возможности');
  });
});
