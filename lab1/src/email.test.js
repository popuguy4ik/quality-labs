import { describe, it, expect } from 'vitest';
import { validateEmail } from './email.js';

describe('validateEmail', () => {
  it.each(['user@example.com', 'ilya.gugu@mail.ru', 'a_b-c+tag@sub.domain.org', 'X@Y.IO'])(
    'accepts valid address %s',
    (email) => {
      expect(validateEmail(email)).toBe(true);
    },
  );

  it('trims spaces around the address', () => {
    expect(validateEmail('  user@example.com ')).toBe(true);
  });

  it.each([
    ['', 'empty string'],
    ['userexample.com', 'no @'],
    ['user@@example.com', 'two @'],
    ['@example.com', 'empty local part'],
    ['user@', 'empty domain'],
    ['user@example', 'domain without dot'],
    ['user@example.c', 'one-letter TLD'],
    ['us er@example.com', 'space inside'],
    ['.user@example.com', 'local part starts with dot'],
    ['user..name@example.com', 'two dots in a row'],
    ['user@-example.com', 'domain label starts with hyphen'],
  ])('rejects %s (%s)', (email) => {
    expect(validateEmail(email)).toBe(false);
  });

  it('rejects local part longer than 64 characters', () => {
    expect(validateEmail('a'.repeat(65) + '@example.com')).toBe(false);
  });

  it('rejects non-string values', () => {
    expect(validateEmail(null)).toBe(false);
    expect(validateEmail(undefined)).toBe(false);
    expect(validateEmail(42)).toBe(false);
  });
});
