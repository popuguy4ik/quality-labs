"""Задание 1: зависимость задержки от числа виртуальных пользователей (jsonplaceholder)."""
import json, statistics as st
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pts, vus = [], []
for line in open('results/load-jsonplaceholder.json'):
    d = json.loads(line)
    if d.get('type') != 'Point':
        continue
    t = datetime.fromisoformat(d['data']['time']).timestamp()
    if d['metric'] == 'http_req_duration':
        pts.append((t, d['data']['value'], d['data']['tags'].get('name')))
    elif d['metric'] == 'vus':
        vus.append((t, d['data']['value']))
t0 = min(p[0] for p in pts)
vus.sort()

def vu_at(t):
    v = 0
    for tt, vv in vus:
        if tt > t: break
        v = vv
    return v

levels = {}
for t, val, name in pts:
    v = vu_at(t)
    if v in (1, 5, 10, 20, 30):
        levels.setdefault(v, []).append((val, name))
rows = []
for v in sorted(levels):
    vals = sorted(x for x, _ in levels[v])
    q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))]
    by = {n: st.median([x for x, nn in levels[v] if nn == n]) for n in ('GET /posts', 'GET /posts/1', 'POST /posts')}
    rows.append({'vus': v, 'n': len(vals), 'avg': st.mean(vals), 'p50': q(0.5), 'p95': q(0.95), 'p99': q(0.99), **by})
for r in rows:
    print({k: round(v, 1) if isinstance(v, float) else v for k, v in r.items()})
json.dump(rows, open('results/load-by-vus.json', 'w'), ensure_ascii=False)

# Рисунок размером 16 × 8 см: шрифт в пунктах совпадает с размером на странице отчета
fig, ax = plt.subplots(figsize=(16 / 2.54, 8 / 2.54), dpi=200)
x = [r['vus'] for r in rows]
ax.plot(x, [r['p50'] for r in rows], 'o-', label='медиана (p50)', color='#4F46E5', lw=1.6)
ax.plot(x, [r['p95'] for r in rows], 's-', label='p95', color='#F59E0B', lw=1.6)
ax.plot(x, [r['p99'] for r in rows], '^--', label='p99', color='#CE2C31', lw=1.2)
ax.axhline(500, color='#57536E', lw=0.8, ls=':')
ax.text(30, 480, 'порог p95 = 500 мс', ha='right', va='top', fontsize=8, color='#57536E')
ax.set_xlabel('Виртуальные пользователи (VU)', fontsize=9)
ax.set_ylabel('Время ответа, мс', fontsize=9)
ax.set_xticks(x)
ax.set_ylim(0, 520)
ax.grid(alpha=0.3)
ax.tick_params(labelsize=8)
ax.legend(fontsize=8, loc='center right')
fig.tight_layout()
fig.savefig('results/load-latency-vs-vus.png')
print('saved')
