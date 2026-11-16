import http from 'k6/http';
import { check, sleep } from 'k6';
// Короткий прогон для веб-дашборда k6 (шаг 4)
export const options = { stages: [{ duration: '20s', target: 10 }, { duration: '30s', target: 10 }, { duration: '10s', target: 0 }] };
export default function () {
  const r = http.get('https://jsonplaceholder.typicode.com/posts');
  check(r, { 'status 200': (x) => x.status === 200 });
  sleep(1);
}
