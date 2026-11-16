import http from 'k6/http';
import { check, sleep } from 'k6';

// Soak-тест: 30 минут постоянной нагрузки, ищем рост памяти и деградацию
export const options = {
  scenarios: {
    soak: { executor: 'constant-vus', vus: 20, duration: '30m' },
  },
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8091';

export default function () {
  if (Math.random() < 0.7) {
    const r = http.get(`${BASE_URL}/api/products`, { tags: { name: 'products' } });
    check(r, { 'products 200': (x) => x.status === 200 });
  } else {
    const r = http.post(`${BASE_URL}/api/auth`, JSON.stringify({ email: `u${__VU}@test.local`, password: 'secret' }), {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'auth' },
    });
    check(r, { 'auth 200': (x) => x.status === 200 });
  }
  sleep(0.5);
}
