"""Сборка единого отчета: каждая лабораторная работа становится отдельным разделом."""
import re
from pathlib import Path

HERE = Path(__file__).parent
PENDING = '*[Результат запуска в GitHub Actions будет добавлен после публикации репозитория.]*'

HEAD = '''---
ministry: "Министерство науки и высшего образования Российской Федерации"
university: "Наименование учебного заведения"
faculty: "Факультет информационных технологий"
department: "Кафедра программной инженерии"
work_type: "по лабораторным работам"
work_number: "1–5"
discipline: "Управление качеством"
topic: "Контроль качества веб-приложения: тестирование, аудит и непрерывная интеграция"
student: "Гугучкин И. Е."
group: "ПРО-ИТ-104М"
teacher: "Фамилия И. О."
city: "Город"
year: "2026"
date: "22.11.2026"
title_page: full
section_page_break: structural
---

# СОДЕРЖАНИЕ

{{toc}}

'''


def front(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    meta = dict(re.findall(r'^(\w+): "(.*)"$', m.group(1), re.M))
    return meta, text[m.end():]


out = [HEAD]
for n in range(1, 6):
    meta, body = front((HERE / f'lab{n}.md').read_text())
    p = f'l{n}-'
    # уникальные метки и ссылки внутри общего документа
    body = re.sub(r'\{#([\w-]+)', lambda m: '{#' + p + m.group(1), body)
    body = re.sub(r'@(fig|tbl|lst):([\w-]+)', lambda m: f'@{m.group(1)}:{p}{m.group(2)}', body)
    # заголовки: «# 2 Ход работы» -> «## 2.2 Ход работы», «## 2.1 ...» -> «### 2.2.1 ...»
    def head(m):
        level, num, title = len(m.group(1)), m.group(2), m.group(3)
        return '#' * (level + 1) + f' {n}.{num} {title}'
    lines = []
    in_code = False
    for line in body.split('\n'):
        if line.startswith('```'):
            in_code = not in_code
        if not in_code:
            line = re.sub(r'^(#{1,2}) (\d+(?:\.\d+)?) (.*)$', head, line)
        lines.append(line)
    body = '\n'.join(lines)
    body = re.sub(r'%%[A-Z0-9_]+%%', PENDING, body)
    out.append(('{{pagebreak}}\n\n' if n > 1 else '') + f'# {n} Лабораторная работа № {n}. {meta["topic"]}\n\n{body.strip()}\n\n')

(HERE / 'combined.md').write_text(''.join(out))
print('combined.md:', sum(len(x) for x in out), 'chars')
