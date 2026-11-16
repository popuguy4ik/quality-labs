import { test, expect } from '../pages/fixtures';
import { CatalogPage } from '../pages/CatalogPage';
import { CartPage } from '../pages/CartPage';

// Задание 3: тест падает специально, чтобы разобрать trace и видео.
// Ошибка в ожидании: после двух кликов по одному товару ждем количество 1, а в корзине 2.
test('@demo корзина: повторное добавление того же товара', async ({ page }) => {
  const catalog = new CatalogPage(page);
  const cart = new CartPage(page);
  await catalog.goto();
  await catalog.addToCart(0);
  await catalog.addToCart(0);
  await cart.goto();
  await expect(cart.rows.first().locator('.cart_quantity button')).toHaveText('1');
});
