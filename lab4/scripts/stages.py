"""Разбивка результатов k6 (--out json) по ступеням нагрузки: p50/p95, ошибки, фактический RPS."""
import json, sys, statistics as st
from datetime import datetime

path, plan = sys.argv[1], [int(x) for x in sys.argv[2].split(',')]
ramp, hold = int(sys.argv[3]), int(sys.argv[4])
pts = []
for line in open(path):
    d = json.loads(line)
    if d.get('type') != 'Point' or d['metric'] not in ('http_req_duration', 'http_req_failed'):
        continue
    t = datetime.fromisoformat(d['data']['time']).timestamp()
    pts.append((t, d['metric'], d['data']['value']))
t0 = min(p[0] for p in pts)
rows = []
start = 10  # первые 10 с — разгон до первой ступени
for i, rate in enumerate(plan):
    a = t0 + start + i * (ramp + hold) + ramp
    b = a + hold
    dur = sorted(v for t, m, v in pts if m == 'http_req_duration' and a <= t < b)
    fail = [v for t, m, v in pts if m == 'http_req_failed' and a <= t < b]
    if not dur:
        break
    p = lambda q: dur[min(len(dur) - 1, int(q * len(dur)))]
    rows.append({'target': rate, 'rps': round(len(dur) / hold, 1), 'p50': round(p(0.5), 1), 'p95': round(p(0.95), 1), 'p99': round(p(0.99), 1), 'errors': round(100 * sum(fail) / max(1, len(fail)), 2)})
for r in rows:
    print(r)
json.dump(rows, open(path.replace('.json', '-stages.json'), 'w'))
