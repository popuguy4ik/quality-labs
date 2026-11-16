import { describe, it, expect } from 'vitest';
import { formatCurrency } from './format.js';

// Intl ставит неразрывный пробел между разрядами и перед знаком валюты
const NBSP = ' ';

describe('formatCurrency', () => {
  it('formats rubles with two decimals', () => {
    expect(formatCurrency(1234.5, 'RUB')).toBe(`1${NBSP}234,50${NBSP}₽`);
  });

  it('uses rubles by default', () => {
    expect(formatCurrency(100)).toBe(`100,00${NBSP}₽`);
  });

  it('formats dollars and euros', () => {
    expect(formatCurrency(99.9, 'USD')).toBe(`99,90${NBSP}$`);
    expect(formatCurrency(99.9, 'EUR')).toBe(`99,90${NBSP}€`);
  });

  it('formats zero', () => {
    expect(formatCurrency(0, 'RUB')).toBe(`0,00${NBSP}₽`);
  });

  it('formats negative amounts', () => {
    expect(formatCurrency(-250, 'RUB')).toBe(`-250,00${NBSP}₽`);
  });

  it('rounds to kopecks', () => {
    expect(formatCurrency(10.456, 'RUB')).toBe(`10,46${NBSP}₽`);
  });

  it('formats millions with grouping', () => {
    expect(formatCurrency(1000000, 'RUB')).toBe(`1${NBSP}000${NBSP}000,00${NBSP}₽`);
  });

  it('throws for invalid amount', () => {
    expect(() => formatCurrency('100', 'RUB')).toThrow('Amount must be a finite number');
    expect(() => formatCurrency(NaN, 'RUB')).toThrow('Amount must be a finite number');
    expect(() => formatCurrency(Infinity, 'RUB')).toThrow('Amount must be a finite number');
  });

  it('throws for unsupported currency', () => {
    expect(() => formatCurrency(10, 'GBP')).toThrow('Unsupported currency: GBP');
  });
});
