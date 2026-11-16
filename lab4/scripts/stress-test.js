import http from 'k6/http';
import { check } from 'k6';

// Stress-тест: поднимаем интенсивность запросов, пока сервис не начнет отказывать.
// Открытая модель нагрузки: запросы приходят с заданной частотой, даже если сервер не успевает.
const RATES = (__ENV.RATES || '100,200,300,400,500,600,800,1000,1500').split(',').map(Number);
export const options = {
  scenarios: {
    stress: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      maxVUs: 1500,
      stages: RATES.flatMap((r) => [{ duration: '10s', target: r }, { duration: '30s', target: r }]),
    },
  },
  thresholds: {
    // Точка отказа: тест останавливается, если p95 > 1 c или ошибок больше 5%
    http_req_duration: [{ threshold: 'p(95)<1000', abortOnFail: true, delayAbortEval: '20s' }],
    http_req_failed: [{ threshold: 'rate<0.05', abortOnFail: true, delayAbortEval: '20s' }],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8090';

export default function () {
  if (Math.random() < 0.7) {
    const r = http.get(`${BASE_URL}/api/products`, { tags: { name: 'products' }, timeout: '10s' });
    check(r, { 'products 200': (x) => x.status === 200 });
  } else {
    const r = http.post(`${BASE_URL}/api/auth`, JSON.stringify({ email: 'stress@test.local', password: 'secret' }), {
      headers: { 'Content-Type': 'application/json' }, tags: { name: 'auth' }, timeout: '10s',
    });
    check(r, { 'auth 200': (x) => x.status === 200 });
  }
}
