import { test, expect } from '../pages/fixtures';
import { LoginPage } from '../pages/LoginPage';
import { CatalogPage } from '../pages/CatalogPage';
import { CartPage } from '../pages/CartPage';
import { newUser } from './user';

test.describe('Интернет-магазин automationexercise.com', () => {
  test('1. регистрация нового пользователя', async ({ page }, info) => {
    const login = new LoginPage(page);
    const user = newUser(info.project.name);
    await login.goto();
    await login.register(user);

    await expect(page.locator('[data-qa="account-created"]')).toHaveText(/account created/i);
    await page.locator('[data-qa="continue-button"]').click();
    await expect(page.getByText(`Logged in as ${user.name}`)).toBeVisible();

    await login.deleteAccount();
    await expect(page.locator('[data-qa="account-deleted"]')).toHaveText(/account deleted/i);
  });

  test('2. поиск товара', async ({ page }) => {
    const catalog = new CatalogPage(page);
    await catalog.goto();
    await catalog.search('Jeans');

    await expect(catalog.title).toHaveText(/searched products/i);
    const names = await catalog.productNames();
    expect(names.length).toBeGreaterThan(0);
    for (const n of names) expect(n.toLowerCase()).toContain('jeans');
  });

  test('3. добавление в корзину', async ({ page }) => {
    const catalog = new CatalogPage(page);
    const cart = new CartPage(page);
    await catalog.goto();
    const names = await catalog.productNames();
    await catalog.addToCart(0);
    await catalog.addToCart(1);

    await cart.goto();
    await expect(cart.rows).toHaveCount(2);
    for (const name of names.slice(0, 2)) {
      const row = cart.row(name);
      await expect(row.locator('.cart_quantity button')).toHaveText('1');
      const price = await row.locator('.cart_price').innerText();
      await expect(row.locator('.cart_total_price')).toHaveText(price);
    }
  });

  test('4. оформление заказа', async ({ page }, info) => {
    const login = new LoginPage(page);
    const catalog = new CatalogPage(page);
    const cart = new CartPage(page);
    const user = newUser(info.project.name);
    await login.goto();
    await login.register(user);
    await page.locator('[data-qa="continue-button"]').click();

    await catalog.goto();
    const [first] = await catalog.productNames();
    await catalog.addToCart(0);
    await cart.goto();
    await cart.checkoutButton.click();

    await expect(page).toHaveURL(/checkout/);
    await expect(page.locator('#address_delivery')).toContainText('Toronto');
    await expect(page.locator('#cart_info')).toContainText(first);
    await page.locator('textarea[name="message"]').fill('Тестовый заказ, ЛР2');
    await page.getByRole('link', { name: 'Place Order' }).click();
    // Платежные данные на чужом сайте не вводим: проверяем, что открылась страница оплаты
    await expect(page).toHaveURL(/payment/);
    await expect(page.locator('[data-qa="pay-button"]')).toBeVisible();

    await login.deleteAccount();
  });

  test('5. выход из аккаунта', async ({ page }, info) => {
    const login = new LoginPage(page);
    const user = newUser(info.project.name);
    await login.goto();
    await login.register(user);
    await page.locator('[data-qa="continue-button"]').click();
    await expect(page.getByText(`Logged in as ${user.name}`)).toBeVisible();

    await login.logout();
    await expect(page).toHaveURL(/login/);
    await expect(page.getByRole('link', { name: 'Signup / Login' })).toBeVisible();
    await expect(page.getByText(`Logged in as ${user.name}`)).toHaveCount(0);

    await login.login(user.email, user.password);
    await login.deleteAccount();
  });
});
