"""Двухпроходная сборка единого отчета со статическим содержанием."""
import json, os, re, subprocess
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / 'out'
NAME = 'Отчёт_ЛР1-5_Управление_качеством'
subprocess.run(['python3', 'combine.py'], cwd=HERE, check=True, capture_output=True)
heads = []
for line in (HERE / 'combined.md').read_text().split('\n'):
    m = re.match(r'^(#{1,2}) (\d.*)$', line)
    if m:
        heads.append((len(m.group(1)), m.group(2)))
toc = HERE / 'toc.json'

def build():
    env = dict(os.environ, TOC_JSON=str(toc))
    subprocess.run(['python3', 'md2docx.py', 'combined.md', '-o', f'out/{NAME}.docx'], cwd=HERE, env=env, check=True, capture_output=True)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', f'{NAME}.docx'], cwd=OUT, check=True, capture_output=True)

def pages():
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', f'{NAME}.pdf'], cwd=OUT, capture_output=True, text=True).stdout).group(1))
    texts = [subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), f'{NAME}.pdf', '-'], cwd=OUT, capture_output=True, text=True).stdout for i in range(1, n + 1)]
    res, start = [], 3
    norm = lambda s: re.sub(r'\s+', ' ', s).replace('-', '')
    for level, text in heads:
        key = norm(text)[:40]
        for i in range(start, n + 1):
            if key in norm(texts[i - 1]):
                res.append((level, text, i)); start = i; break
        else:
            res.append((level, text, '?'))
    return res

toc.write_text(json.dumps([(l, t, 0) for l, t in heads], ensure_ascii=False))
build()
for _ in range(2):
    entries = pages()
    toc.write_text(json.dumps(entries, ensure_ascii=False))
    build()
print('pages ok:', sum(1 for e in entries if e[2] != '?'), 'of', len(entries))
