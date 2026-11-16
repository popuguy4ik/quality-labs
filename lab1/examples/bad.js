var discount = 10;
let total = 100;
const unused = 'не используется';

export function check(price) {
  if (price == '100') {
    console.log('сто');
  }
  return total - discount;
}
