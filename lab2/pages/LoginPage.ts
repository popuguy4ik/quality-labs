import { Page, Locator } from '@playwright/test';

export type User = { name: string; email: string; password: string };

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;
  readonly signupName: Locator;
  readonly signupEmail: Locator;
  readonly signupButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('[data-qa="login-email"]');
    this.passwordInput = page.locator('[data-qa="login-password"]');
    this.submitButton = page.locator('[data-qa="login-button"]');
    this.errorMessage = page.getByText('Your email or password is incorrect!');
    this.signupName = page.locator('[data-qa="signup-name"]');
    this.signupEmail = page.locator('[data-qa="signup-email"]');
    this.signupButton = page.locator('[data-qa="signup-button"]');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  // Регистрация: имя и почта на странице входа, остальное на странице анкеты
  async register(user: User) {
    await this.signupName.fill(user.name);
    await this.signupEmail.fill(user.email);
    await this.signupButton.click();
    const p = this.page;
    await p.locator('#id_gender1').check();
    await p.locator('[data-qa="password"]').fill(user.password);
    await p.locator('[data-qa="days"]').selectOption('15');
    await p.locator('[data-qa="months"]').selectOption('5');
    await p.locator('[data-qa="years"]').selectOption('1998');
    await p.locator('[data-qa="first_name"]').fill('Ilya');
    await p.locator('[data-qa="last_name"]').fill('Testov');
    await p.locator('[data-qa="address"]').fill('Test street 1');
    await p.locator('[data-qa="country"]').selectOption('Canada');
    await p.locator('[data-qa="state"]').fill('Ontario');
    await p.locator('[data-qa="city"]').fill('Toronto');
    await p.locator('[data-qa="zipcode"]').fill('M5V 2T6');
    await p.locator('[data-qa="mobile_number"]').fill('+10000000000');
    await p.locator('[data-qa="create-account"]').click();
  }

  async deleteAccount() {
    await this.page.goto('/delete_account');
  }

  async logout() {
    await this.page.getByRole('link', { name: 'Logout' }).click();
  }
}
