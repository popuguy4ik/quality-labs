const SUPPORTED = ['RUB', 'USD', 'EUR'];

export const formatCurrency = (amount, currency = 'RUB') => {
  if (typeof amount !== 'number' || !Number.isFinite(amount)) {
    throw new Error('Amount must be a finite number');
  }
  if (!SUPPORTED.includes(currency)) {
    throw new Error(`Unsupported currency: ${currency}`);
  }
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};
