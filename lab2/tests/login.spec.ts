import { test, expect } from '../pages/fixtures';
import { LoginPage } from '../pages/LoginPage';
import { newUser } from './user';

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ page }, info) => {
    const loginPage = new LoginPage(page);
    const user = newUser(info.project.name);
    await loginPage.goto();
    await loginPage.register(user);
    await page.locator('[data-qa="continue-button"]').click();
    await loginPage.logout();

    await loginPage.login(user.email, user.password);
    await expect(page).toHaveURL('/');
    await expect(page.getByText(`Logged in as ${user.name}`)).toBeVisible();
    await loginPage.deleteAccount();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    // Адрес случайный: фиксированный wrong@example.com на общем стенде кто-то уже зарегистрировал
    await loginPage.login(`nobody.${Date.now()}@example.com`, 'wrongpass');

    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('incorrect');
  });

  test('should validate empty fields', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.submitButton.click();

    await expect(page).toHaveURL(/login/);
    const valid = await loginPage.emailInput.evaluate((el: HTMLInputElement) => el.checkValidity());
    expect(valid).toBe(false);
  });
});
