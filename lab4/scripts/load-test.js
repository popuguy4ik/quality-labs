import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Кастомные метрики
const errorRate = new Rate('errors');
const createDuration = new Trend('create_duration');

// Ступенчатая нагрузка: на каждой ступени 30 секунд держим одно число VU,
// чтобы потом построить зависимость задержки от количества пользователей
export const options = {
  stages: [
    { duration: '10s', target: 1 }, { duration: '30s', target: 1 },
    { duration: '5s', target: 5 }, { duration: '30s', target: 5 },
    { duration: '5s', target: 10 }, { duration: '30s', target: 10 },
    { duration: '5s', target: 20 }, { duration: '30s', target: 20 },
    { duration: '5s', target: 30 }, { duration: '30s', target: 30 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% запросов быстрее 500 мс
    errors: ['rate<0.01'],            // меньше 1% ошибок
  },
};

const BASE_URL = 'https://jsonplaceholder.typicode.com';

export default function () {
  // 1. Список постов
  const list = http.get(`${BASE_URL}/posts`, { tags: { name: 'GET /posts' } });
  check(list, {
    'posts status is 200': (r) => r.status === 200,
    'posts has 100 items': (r) => r.json().length === 100,
  });
  errorRate.add(list.status !== 200);

  // 2. Один пост
  const one = http.get(`${BASE_URL}/posts/1`, { tags: { name: 'GET /posts/1' } });
  check(one, { 'post status is 200': (r) => r.status === 200 });
  errorRate.add(one.status !== 200);

  // 3. Создание поста (API имитирует запись и возвращает 201)
  const res = http.post(`${BASE_URL}/posts`, JSON.stringify({ title: 'k6', body: 'load test', userId: 1 }), {
    headers: { 'Content-Type': 'application/json; charset=UTF-8' },
    tags: { name: 'POST /posts' },
  });
  createDuration.add(res.timings.duration);
  check(res, { 'create status is 201': (r) => r.status === 201 });
  errorRate.add(res.status !== 201);

  sleep(1);
}
