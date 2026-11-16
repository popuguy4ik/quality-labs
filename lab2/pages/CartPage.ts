import { Page, Locator } from '@playwright/test';

export class CartPage {
  readonly page: Page;
  readonly rows: Locator;
  readonly checkoutButton: Locator;
  readonly emptyMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.rows = page.locator('#cart_info_table tbody tr');
    this.checkoutButton = page.getByText('Proceed To Checkout');
    this.emptyMessage = page.locator('#empty_cart');
  }

  async goto() {
    await this.page.goto('/view_cart');
  }

  row(name: string) {
    return this.rows.filter({ hasText: name });
  }

  async removeAll() {
    while ((await this.rows.count()) > 0) {
      await this.rows.first().locator('.cart_quantity_delete').click();
      await this.page.waitForTimeout(500);
    }
  }
}
