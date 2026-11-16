// Учебный API для нагрузочного тестирования (без зависимостей)
import http from 'node:http';
import crypto from 'node:crypto';

const PORT = process.env.PORT || 8080;
const LEAK = process.env.LEAK === '1';
const SESSION_TTL = 60_000;
const sessions = new Map();

const products = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  name: `Товар ${i + 1}`,
  price: 100 + ((i * 37) % 900),
}));

function json(res, code, body) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve) => {
    let data = '';
    req.on('data', (c) => (data += c));
    req.on('end', () => resolve(data));
  });
}

// Исправленная версия: просроченные сессии удаляются раз в 10 секунд
if (!LEAK) {
  setInterval(() => {
    const now = Date.now();
    for (const [token, s] of sessions) if (now - s.created > SESSION_TTL) sessions.delete(token);
  }, 10_000).unref();
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  if (url.pathname === '/health') return json(res, 200, { ok: true });
  if (url.pathname === '/metrics') {
    const m = process.memoryUsage();
    return json(res, 200, { rss: m.rss, heapUsed: m.heapUsed, sessions: sessions.size, leak: LEAK });
  }
  if (req.method === 'GET' && url.pathname === '/api/products') return json(res, 200, products);
  const match = url.pathname.match(/^\/api\/products\/(\d+)$/);
  if (req.method === 'GET' && match) {
    const p = products.find((x) => x.id === Number(match[1]));
    return p ? json(res, 200, p) : json(res, 404, { error: 'Not found' });
  }
  if (req.method === 'POST' && url.pathname === '/api/auth') {
    let body;
    try { body = JSON.parse(await readBody(req)); } catch { return json(res, 400, { error: 'Bad JSON' }); }
    if (!body.email || !body.password) return json(res, 400, { error: 'Email and password required' });
    // Хеширование пароля нагружает процессор, как в настоящей авторизации
    crypto.pbkdf2Sync(body.password, body.email, 20_000, 32, 'sha256');
    const token = crypto.randomBytes(16).toString('hex');
    // Ошибка, которую ищет soak-тест: в режиме LEAK сессии никогда не удаляются
    sessions.set(token, { email: body.email, created: Date.now(), profile: crypto.randomBytes(3072).toString('base64') });
    return json(res, 200, { token });
  }
  json(res, 404, { error: 'Not found' });
});

server.listen(PORT, () => console.log(`API on :${PORT}, leak=${LEAK}`));
