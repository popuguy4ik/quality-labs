"""Задание 2: фактическая пропускная способность и p95 в зависимости от заданной интенсивности."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

a = json.load(open('results/stress-stages.json'))
b = json.load(open('results/stress2-stages.json'))
rows = [r for r in a if r['target'] < 1000] + b
rows.sort(key=lambda r: r['target'])
json.dump(rows, open('results/stress-all-stages.json', 'w'))
x = [r['target'] for r in rows]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5 / 2.54, 7 / 2.54), dpi=200)
ax1.plot(x, x, ':', color='#A9A5CC', lw=1, label='идеал (сколько подано)')
ax1.plot(x, [r['rps'] for r in rows], 'o-', color='#4F46E5', lw=1.6, ms=4, label='обработано')
ax1.axvspan(1000, 2000, color="#F59E0B", alpha=0.10); ax1.axvspan(2000, 4000, color="#CE2C31", alpha=0.10)
ax1.set_xlabel('Подано, запросов/с', fontsize=8)
ax1.set_ylabel('Обработано, запросов/с', fontsize=8)
ax1.legend(fontsize=7, loc='upper left', frameon=False)
ax1.tick_params(labelsize=7)
ax1.grid(alpha=0.3)

ax2.plot(x, [r['p95'] for r in rows], 's-', color='#F59E0B', lw=1.6, ms=4, label='p95')
ax2.plot(x, [r['p50'] for r in rows], 'o-', color='#4F46E5', lw=1.2, ms=3, label='медиана')
ax2.set_yscale('log')
ax2.axhline(1000, color='#57536E', ls=':', lw=0.8)
ax2.text(120, 1150, 'порог 1 с', fontsize=7, color='#57536E')
ax2.axvspan(1000, 2000, color="#F59E0B", alpha=0.10); ax2.axvspan(2000, 4000, color="#CE2C31", alpha=0.10)
ax2.set_xlabel('Подано, запросов/с', fontsize=8)
ax2.set_ylabel('Время ответа, мс (лог. шкала)', fontsize=8)
ax2.legend(fontsize=7, loc='upper left', frameon=False)
ax2.tick_params(labelsize=7)
ax2.grid(alpha=0.3, which='both')
fig.tight_layout()
fig.savefig('results/stress-degradation.png')
for r in rows: print(r)
