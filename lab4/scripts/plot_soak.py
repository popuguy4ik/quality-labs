"""Задание 3: память и время ответа во время soak-теста (утечка и исправление)."""
import csv, json
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def mem(v):
    rows = [r for r in csv.DictReader(open(f'results/soak-{v}-memory.csv')) if r['heap_mb']]
    return [int(r['t']) / 60 for r in rows], [float(r['heap_mb']) for r in rows], [int(r['sessions']) for r in rows]

def p95_windows(v, win=300):
    pts = []
    for line in open(f'results/soak-{v}.json'):
        d = json.loads(line)
        if d.get('type') == 'Point' and d['metric'] == 'http_req_duration':
            pts.append((datetime.fromisoformat(d['data']['time']).timestamp(), d['data']['value']))
    t0 = min(p[0] for p in pts)
    out = []
    for k in range(6):
        vals = sorted(x for t, x in pts if k * win <= t - t0 < (k + 1) * win)
        out.append((k * 5 + 2.5, vals[int(0.95 * len(vals))], vals[len(vals) // 2]))
    return out

res = {}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5 / 2.54, 7 / 2.54), dpi=200)
for v, color, label in (('leak', '#CE2C31', 'с утечкой'), ('fixed', '#4F46E5', 'исправленная')):
    t, heap, sess = mem(v)
    ax1.plot(t, heap, color=color, lw=1.6, label=label)
    w = p95_windows(v)
    ax2.plot([x[0] for x in w], [x[1] for x in w], 'o-', color=color, lw=1.4, ms=3, label=label)
    res[v] = {'heap_start': heap[0], 'heap_end': heap[-1], 'sessions_end': sess[-1], 'p95_windows': [round(x[1], 2) for x in w], 'p50_windows': [round(x[2], 2) for x in w]}
ax1.set_xlabel('Время теста, мин', fontsize=8); ax1.set_ylabel('Занятая куча, МБ', fontsize=8)
ax2.set_xlabel('Время теста, мин (окна по 5 мин)', fontsize=8); ax2.set_ylabel('p95 времени ответа, мс', fontsize=8)
ax2.set_ylim(0, 25)
for ax in (ax1, ax2):
    ax.tick_params(labelsize=7); ax.grid(alpha=0.3); ax.legend(fontsize=7, frameon=False, loc='upper left')
fig.tight_layout()
fig.savefig('results/soak.png')
json.dump(res, open('results/soak-analysis.json', 'w'))
print(json.dumps(res, ensure_ascii=False))
