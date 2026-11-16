import type { User } from '../pages/LoginPage';

export const newUser = (tag: string): User => ({
  name: 'Ilya Tester',
  email: `qa.${tag}.${Date.now()}.${Math.floor(Math.random() * 1e4)}@example.com`,
  password: 'Qa-lab2-Pass!',
});
