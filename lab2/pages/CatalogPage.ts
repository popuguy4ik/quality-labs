import { Page, Locator } from '@playwright/test';

export class CatalogPage {
  readonly page: Page;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly title: Locator;
  readonly products: Locator;
  readonly modal: Locator;

  constructor(page: Page) {
    this.page = page;
    this.searchInput = page.locator('#search_product');
    this.searchButton = page.locator('#submit_search');
    this.title = page.locator('.features_items h2.title');
    this.products = page.locator('.features_items .productinfo');
    this.modal = page.locator('#cartModal');
  }

  async goto() {
    await this.page.goto('/products');
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
  }

  productNames() {
    return this.products.locator('p').allTextContents();
  }

  // Добавить товар по номеру карточки и закрыть окно «Added!»
  async addToCart(index: number) {
    await this.products.nth(index).locator('.add-to-cart').click();
    await this.modal.getByRole('button', { name: 'Continue Shopping' }).click();
  }
}
