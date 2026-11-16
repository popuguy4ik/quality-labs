#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор отчёта .docx из Markdown с оформлением по ГОСТ 7.32-2017.

Запуск:
    python3 md2docx.py report.md -o report.docx

Требования: python-docx, PyYAML  (pip install python-docx PyYAML)

Поддерживаемый синтаксис Markdown
---------------------------------
    ---                       YAML-преамбула; ключ title_page задаёт шапку:
                              full (титульный лист), compact (3-4 строки), none;
                              work_type задаёт вид работы («Доклад», «Реферат»);
                              section_page_break: false — разделы идут подряд
    # Заголовок               раздел 1-го уровня
    ## Заголовок              подраздел 2-го уровня
    {{toc}}                   поле «СОДЕРЖАНИЕ» (обновляется в Word клавишей F9)
    {{pagebreak}}             разрыв страницы
    ![Подпись](img/a.png){#label width=16cm}      рисунок с автонумерацией
    Таблица: {#label} Подпись                     подпись к идущей ниже таблице
    | a | b |                                     таблица GFM
    Листинг: {#label} Подпись                     подпись к идущему ниже листингу
    ```js ... ```                                 листинг кода
    - пункт / 1. пункт                            списки
    **жирный**, *курсив*, `моноширинный`          форматирование в строке
    @fig:label, @tbl:label, @lst:label            ссылки на номер объекта

Заголовки структурных элементов (СОДЕРЖАНИЕ, ВВЕДЕНИЕ, ЗАКЛЮЧЕНИЕ,
СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ, ПРИЛОЖЕНИЕ …) печатаются прописными
буквами по центру и начинаются с новой страницы — как требует ГОСТ.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import yaml
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

# ────────────────────────────── параметры ГОСТ 7.32-2017 ──────────────────────
FONT = "Times New Roman"          # основной шрифт
FONT_SIZE = Pt(14)                # кегль основного текста
MONO = "Courier New"              # шрифт листингов
MONO_SIZE = Pt(10)                # кегль листингов (78 знаков умещаются в строку)
CODE_WRAP = 78                    # перенос слишком длинных строк кода
LINE_SPACING = 1.5                # полуторный междустрочный интервал
FIRST_INDENT = Cm(1.25)           # абзацный отступ
TABLE_FONT_SIZE = Pt(12)          # кегль внутри таблиц
CAPTION_SIZE = Pt(14)             # кегль подписей к рисункам и таблицам
MARGINS = dict(left=Mm(30), right=Mm(10), top=Mm(20), bottom=Mm(20))
DEFAULT_IMG_WIDTH = Cm(16.0)      # ширина рисунка по умолчанию
TITLE_TAIL_LINES = 12             # отступ до строки «Город Год» на титуле
BULLET = "\u2013"                 # маркер перечисления (короткое тире)

# Заголовки, которые ГОСТ относит к структурным элементам отчёта
STRUCTURAL = (
    "СОДЕРЖАНИЕ", "ОГЛАВЛЕНИЕ", "РЕФЕРАТ", "ВВЕДЕНИЕ", "ЗАКЛЮЧЕНИЕ",
    "ВЫВОД", "ВЫВОДЫ",
    "СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "СПИСОК ЛИТЕРАТУРЫ",
    "ПРИЛОЖЕНИЕ", "ОПРЕДЕЛЕНИЯ", "ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ",
)

# ────────────────────────────────── разбор Markdown ───────────────────────────
RE_ATTRS = re.compile(r"\{([^}]*)\}\s*$")
RE_LABEL = re.compile(r"#([\w-]+)")
RE_IMAGE = re.compile(r"^!\[(?P<cap>.*?)\]\((?P<src>[^)]+)\)(?P<attrs>\s*\{[^}]*\})?\s*$")
RE_CAPTION = re.compile(r"^(?P<kind>Таблица|Листинг):\s*(?P<attrs>\{[^}]*\}\s*)?(?P<text>.+)$")
RE_ULI = re.compile(r"^[-*]\s+(.*)$")
RE_OLI = re.compile(r"^\d+[.)]\s+(.*)$")
RE_REF = re.compile(r"@(fig|tbl|lst):([\w-]+)")


def parse_attrs(raw: str | None) -> dict:
    """Разбирает хвост вида {#label width=16cm}."""
    out: dict[str, str] = {}
    if not raw:
        return out
    body = raw.strip().strip("{}")
    for token in body.split():
        if token.startswith("#"):
            out["label"] = token[1:]
        elif "=" in token:
            k, v = token.split("=", 1)
            out[k] = v
    return out


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = yaml.safe_load(text[3:end]) or {}
    return meta, text[end + 4:].lstrip("\n")


def tokenize(md: str) -> list[dict]:
    """Превращает Markdown в плоский список блоков."""
    lines = md.split("\n")
    blocks: list[dict] = []
    i, pending_caption = 0, None

    def take_caption():
        nonlocal pending_caption
        c, pending_caption = pending_caption, None
        return c or {}

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == "{{toc}}":
            blocks.append({"type": "toc"}); i += 1; continue

        if stripped == "{{pagebreak}}":
            blocks.append({"type": "pagebreak"}); i += 1; continue

        # подпись к следующей таблице или листингу
        m = RE_CAPTION.match(stripped)
        if m and not stripped.startswith("|"):
            attrs = parse_attrs(m.group("attrs"))
            pending_caption = {"kind": m.group("kind"), "text": m.group("text").strip(),
                               "label": attrs.get("label")}
            i += 1
            continue

        # заголовок
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            blocks.append({"type": "heading", "level": level, "text": text})
            i += 1
            continue

        # рисунок
        m = RE_IMAGE.match(stripped)
        if m:
            attrs = parse_attrs(m.group("attrs"))
            blocks.append({"type": "image", "src": m.group("src"),
                           "caption": m.group("cap"), "label": attrs.get("label"),
                           "width": attrs.get("width")})
            i += 1
            continue

        # листинг кода
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            cap = take_caption()
            blocks.append({"type": "code", "lang": lang, "lines": code,
                           "caption": cap.get("text"), "label": cap.get("label")})
            continue

        # таблица GFM
        if stripped.startswith("|"):
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") and c for c in cells):
                    rows.append(cells)
                i += 1
            cap = take_caption()
            blocks.append({"type": "table", "rows": rows,
                           "caption": cap.get("text"), "label": cap.get("label")})
            continue

        # список
        if RE_ULI.match(stripped) or RE_OLI.match(stripped):
            ordered = bool(RE_OLI.match(stripped))
            items: list[str] = []
            while i < len(lines):
                s = lines[i].strip()
                m_u, m_o = RE_ULI.match(s), RE_OLI.match(s)
                if m_o and ordered:
                    items.append(m_o.group(1))
                elif m_u and not ordered:
                    items.append(m_u.group(1))
                elif s and items and not s.startswith(("#", "|", "```", "!", "-")) \
                        and not RE_OLI.match(s):
                    items[-1] += " " + s            # продолжение пункта
                else:
                    break
                i += 1
            blocks.append({"type": "list", "ordered": ordered, "items": items})
            continue

        # обычный абзац
        para: list[str] = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(
                ("#", "|", "```", "!", "- ", "* ", "{{")) \
                and not RE_OLI.match(lines[i].strip()) \
                and not RE_CAPTION.match(lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        if para:
            blocks.append({"type": "para", "text": " ".join(para)})
        else:
            i += 1
    return blocks


def assign_numbers(blocks: list[dict]) -> dict[str, str]:
    """Сквозная нумерация рисунков, таблиц и листингов; возвращает карту меток."""
    refs: dict[str, str] = {}
    counters = {"image": 0, "table": 0, "code": 0}
    prefix = {"image": "fig", "table": "tbl", "code": "lst"}
    for b in blocks:
        if b["type"] in counters:
            # нумеруются только объекты с подписью: служебные врезки
            # (например, дерево каталогов) остаются без номера
            if b["type"] != "image" and not b.get("caption"):
                continue
            counters[b["type"]] += 1
            b["number"] = counters[b["type"]]
            if b.get("label"):
                refs[f"{prefix[b['type']]}:{b['label']}"] = str(b["number"])
    return refs


# ───────────────────────────────── оформление ────────────────────────────────
def set_cell_border(cell, size: int = 4, color: str = "000000") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:color"), color)
        borders.append(el)
    tc_pr.append(borders)


def keep_table_together(table) -> None:
    """Запрещает разрыв строк и переносит таблицу на следующую страницу целиком.

    ГОСТ допускает перенос таблицы с надписью «Продолжение таблицы N»,
    но для коротких таблиц аккуратнее, когда они умещаются на одной странице.
    """
    rows = table.rows
    for i, row in enumerate(rows):
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)
        if i < len(rows) - 1:          # последняя строка не «тянет» за собой текст
            for cell in row.cells:
                for par in cell.paragraphs:
                    par.paragraph_format.keep_with_next = True


def style_base(doc: Document) -> None:
    """Базовые стили документа: шрифт, интервалы, поля страницы."""
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = FONT_SIZE
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.element.rPr.rFonts.set(qn("w:cs"), FONT)
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = LINE_SPACING
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = FIRST_INDENT
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)

    for name, size, bold in (("Heading 1", FONT_SIZE, True),
                             ("Heading 2", FONT_SIZE, True),
                             ("Heading 3", FONT_SIZE, True)):
        st = doc.styles[name]
        st.font.name = FONT
        st.font.size = size
        st.font.bold = bold
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        st.element.rPr.rFonts.set(qn("w:cs"), FONT)
        p = st.paragraph_format
        p.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
        p.line_spacing = LINE_SPACING
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.first_line_indent = FIRST_INDENT
        p.space_before = Pt(12)
        p.space_after = Pt(12)
        p.keep_with_next = True
        p.page_break_before = False

    for sec in doc.sections:
        sec.page_width, sec.page_height = Mm(210), Mm(297)
        sec.left_margin = MARGINS["left"]
        sec.right_margin = MARGINS["right"]
        sec.top_margin = MARGINS["top"]
        sec.bottom_margin = MARGINS["bottom"]


def add_field(paragraph, instr: str, placeholder: str = "") -> None:
    """Вставляет поле Word (PAGE, TOC и т. п.)."""
    r1 = paragraph.add_run()
    fc = OxmlElement("w:fldChar")
    fc.set(qn("w:fldCharType"), "begin")
    fc.set(qn("w:dirty"), "true")
    r1._r.append(fc)

    r2 = paragraph.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r2._r.append(it)

    r3 = paragraph.add_run()
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    r3._r.append(sep)

    if placeholder:
        paragraph.add_run(placeholder)

    r4 = paragraph.add_run()
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    r4._r.append(end)


def enable_update_fields(doc: Document) -> None:
    """Word и LibreOffice обновят СОДЕРЖАНИЕ при открытии файла."""
    settings = doc.settings.element
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


def add_page_numbers(doc: Document, skip_first: bool = True) -> None:
    """Номер страницы внизу по центру.

    skip_first=True — на титульном листе номер не печатается (он входит
    в общую нумерацию, но не проставляется, как требует ГОСТ).
    """
    sec = doc.sections[0]
    if skip_first:
        sec.different_first_page_header_footer = True
        sec.first_page_footer.paragraphs[0].text = ""

    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.first_line_indent = Pt(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    add_field(p, " PAGE ", "2")
    for run in p.runs:
        run.font.name = FONT
        run.font.size = FONT_SIZE


# ───────────────────────────── форматирование текста ─────────────────────────
def add_rich_text(paragraph, text: str, refs: dict[str, str], size=None) -> None:
    """Разбирает **жирный**, *курсив*, `код` и ссылки @fig:label."""
    text = RE_REF.sub(lambda m: refs.get(f"{m.group(1)}:{m.group(2)}", "??"), text)
    for part in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)", text):
        if not part:
            continue
        run = paragraph.add_run()
        if part.startswith("**") and part.endswith("**"):
            run.text, run.bold = part[2:-2], True
        elif part.startswith("*") and part.endswith("*"):
            run.text, run.italic = part[1:-1], True
        elif part.startswith("`") and part.endswith("`"):
            run.text = part[1:-1]
            run.font.name = MONO
            run.font.size = Pt((size or FONT_SIZE).pt - 2)
            run._element.rPr.rFonts.set(qn("w:eastAsia"), MONO)
        else:
            run.text = part
        if run.font.name is None:
            run.font.name = FONT
        if run.font.size is None and size is not None:
            run.font.size = size


def wrap_code(line: str, width: int) -> list[str]:
    """Переносит слишком длинную строку кода, сохраняя отступ."""
    if len(line) <= width:
        return [line]
    indent = len(line) - len(line.lstrip(" "))
    out, rest = [], line
    while len(rest) > width:
        cut = rest.rfind(" ", indent, width)
        if cut <= indent:
            cut = width
        out.append(rest[:cut])
        rest = " " * (indent + 4) + rest[cut:].lstrip(" ")
    out.append(rest)
    return out


# ──────────────────────────────── титульный лист ─────────────────────────────
def build_compact_header(doc: Document, meta: dict) -> None:
    """Короткая шапка на 3-4 строки вместо полного титульного листа."""
    def line(text, *, bold=False, size=FONT_SIZE, after=0):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.first_line_indent = Pt(0)
        pf.line_spacing = 1.0
        pf.space_after = Pt(after)
        run = p.add_run(text)
        run.bold = bold
        run.font.name = FONT
        run.font.size = size

    kind = meta.get("work_type", "Лабораторная работа")
    number = meta.get("work_number")
    line(f"{kind} № {number}" if number else kind, bold=True,
         size=Pt(16), after=4)
    if meta.get("topic"):
        line(f"на тему: «{meta['topic']}»" if meta.get("topic_prefix", True)
             else meta["topic"], bold=True, after=4)
    if meta.get("discipline"):
        line(f"по дисциплине «{meta['discipline']}»", after=4)
    who = ", ".join(x for x in (meta.get("student"), 
                                f"группа {meta['group']}" if meta.get("group") else None)
                    if x)
    if who:
        line(who, after=12)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def build_title_page(doc: Document, meta: dict) -> None:
    def line(text="", *, bold=False, size=FONT_SIZE, align="center",
             spacing=1.0, before=0, after=0, caps=False):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.alignment = {"center": WD_ALIGN_PARAGRAPH.CENTER,
                        "left": WD_ALIGN_PARAGRAPH.LEFT,
                        "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
        pf.first_line_indent = Pt(0)
        pf.line_spacing = spacing
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        if text:
            run = p.add_run(text.upper() if caps else text)
            run.bold = bold
            run.font.name = FONT
            run.font.size = size
        return p

    for key in ("ministry", "university", "faculty", "department"):
        if meta.get(key):
            line(meta[key], caps=(key in ("ministry", "university")))

    for _ in range(6):
        line()

    kind = meta.get("work_type", "Лабораторная работа")
    number = meta.get("work_number")
    line(meta.get("title_word", "ОТЧЁТ"), bold=True, size=Pt(16))
    line(f"{kind} № {number}" if number else kind, size=Pt(14), after=6)
    if meta.get("discipline"):
        line(f"по дисциплине «{meta['discipline']}»", after=12)
    if meta.get("topic"):
        line(f"на тему: «{meta['topic']}»", bold=True)

    for _ in range(6):
        line()

    if meta.get("student"):
        line("Выполнил(а):", align="right")
        line(f"студент(ка) группы {meta.get('group', '')}", align="right")
        line(meta["student"], align="right", after=12)
    if meta.get("teacher"):
        line("Проверил(а):", align="right")
        line(meta["teacher"], align="right")

    # город, год и дата сдачи печатаются в нижней части титульного листа
    for _ in range(TITLE_TAIL_LINES - (1 if meta.get("date") else 0)):
        line()
    if meta.get("date"):
        line(f"Дата сдачи: {meta['date']}", after=6)
    line(f"{meta.get('city', '')} {meta.get('year', '')}".strip())

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ─────────────────────────────────── рендеринг ───────────────────────────────
def render(doc: Document, blocks: list[dict], refs: dict[str, str],
           base_dir: pathlib.Path, break_before_first: bool = True,
           section_break: str = "all") -> None:
    first_section = True
    for b in blocks:
        kind = b["type"]

        if kind == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

        elif kind == "toc":
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_field(p, r' TOC \o "1-2" \h \z \u ',
                      "Содержание обновляется в Word: Ctrl+A, затем F9")
            for run in p.runs:
                run.font.name = FONT
                run.font.size = FONT_SIZE

        elif kind == "heading":
            text = b["text"]
            is_struct = any(text.upper().startswith(s) for s in STRUCTURAL)
            p = doc.add_paragraph(style=f"Heading {min(b['level'], 3)}")
            # ГОСТ 7.32-2017, п. 6.1.3: каждый структурный элемент и каждый
            # раздел основной части начинают с новой страницы. Режим задаётся
            # ключом section_page_break. Первый заголовок разрыв не получает,
            # если титульного листа нет и страница всё равно пуста.
            if b["level"] == 1:
                if section_break == "all":
                    want_break = True
                elif section_break == "structural":
                    want_break = is_struct
                else:
                    want_break = False
                p.paragraph_format.page_break_before = (
                    want_break and not (first_section and not break_before_first))
                first_section = False
            if is_struct:
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.first_line_indent = Pt(0)
                # «ПРИЛОЖЕНИЕ А. Название» — прописными только обозначение
                if text.upper().startswith("ПРИЛОЖЕНИЕ") and ". " in text:
                    designation, title_text = text.split(". ", 1)
                    run = p.add_run(f"{designation.upper()}. {title_text}")
                else:
                    run = p.add_run(text.upper())
            else:
                run = p.add_run(text)
            run.bold = True
            run.font.name = FONT
            run.font.size = FONT_SIZE

        elif kind == "para":
            p = doc.add_paragraph()
            add_rich_text(p, b["text"], refs)

        elif kind == "list":
            for n, item in enumerate(b["items"], 1):
                p = doc.add_paragraph()
                p.paragraph_format.first_line_indent = FIRST_INDENT
                marker = f"{n}) " if b["ordered"] else f"{BULLET} "
                p.add_run(marker).font.name = FONT
                add_rich_text(p, item, refs)

        elif kind == "image":
            src = (base_dir / b["src"]).resolve()
            if not src.exists():
                print(f"  ! файл рисунка не найден: {src}", file=sys.stderr)
                continue
            width = DEFAULT_IMG_WIDTH
            if b.get("width"):
                raw = str(b["width"])
                if raw.endswith("cm"):
                    width = Cm(float(raw[:-2]))
                elif raw.endswith("mm"):
                    width = Mm(float(raw[:-2]))

            p = doc.add_paragraph()
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pf.first_line_indent = Pt(0)
            pf.space_before = Pt(12)
            pf.space_after = Pt(6)
            pf.keep_with_next = True
            p.add_run().add_picture(str(src), width=width)

            cap = doc.add_paragraph()
            cpf = cap.paragraph_format
            cpf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cpf.first_line_indent = Pt(0)
            cpf.space_after = Pt(12)
            add_rich_text(cap, f"Рисунок {b['number']} — {b['caption']}", refs,
                          size=CAPTION_SIZE)
            for run in cap.runs:
                run.font.size = CAPTION_SIZE

        elif kind == "table":
            if b.get("caption"):
                cap = doc.add_paragraph()
                cpf = cap.paragraph_format
                cpf.alignment = WD_ALIGN_PARAGRAPH.LEFT
                cpf.first_line_indent = Pt(0)
                cpf.space_before = Pt(12)
                cpf.space_after = Pt(4)
                cpf.keep_with_next = True
                add_rich_text(cap, f"Таблица {b['number']} — {b['caption']}",
                              refs, size=CAPTION_SIZE)
                for run in cap.runs:
                    run.font.size = CAPTION_SIZE

            rows = b["rows"]
            table = doc.add_table(rows=len(rows), cols=len(rows[0]))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            for r, row in enumerate(rows):
                for c, text in enumerate(row):
                    cell = table.cell(r, c)
                    set_cell_border(cell)
                    p = cell.paragraphs[0]
                    pf = p.paragraph_format
                    pf.first_line_indent = Pt(0)
                    pf.line_spacing = 1.0
                    pf.space_before = Pt(2)
                    pf.space_after = Pt(2)
                    pf.alignment = (WD_ALIGN_PARAGRAPH.CENTER if r == 0
                                    else WD_ALIGN_PARAGRAPH.LEFT)
                    add_rich_text(p, text, refs, size=TABLE_FONT_SIZE)
                    for run in p.runs:
                        run.font.size = TABLE_FONT_SIZE
                        if run.font.name != MONO:
                            run.font.name = FONT
                        if r == 0:
                            run.bold = True
            keep_table_together(table)
            after = doc.add_paragraph()
            after.paragraph_format.space_after = Pt(6)
            after.paragraph_format.line_spacing = 1.0

        elif kind == "code":
            if b.get("caption"):
                cap = doc.add_paragraph()
                cpf = cap.paragraph_format
                cpf.alignment = WD_ALIGN_PARAGRAPH.LEFT
                cpf.first_line_indent = Pt(0)
                cpf.space_before = Pt(12)
                cpf.space_after = Pt(4)
                cpf.keep_with_next = True
                add_rich_text(cap, f"Листинг {b['number']} — {b['caption']}",
                              refs, size=CAPTION_SIZE)
                for run in cap.runs:
                    run.font.size = CAPTION_SIZE

            flat: list[str] = []
            for raw in b["lines"]:
                flat.extend(wrap_code(raw.rstrip(), CODE_WRAP))
            for src_line in flat:
                p = doc.add_paragraph()
                pf = p.paragraph_format
                pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
                pf.first_line_indent = Pt(0)
                pf.line_spacing = 1.0
                pf.space_before = Pt(0)
                pf.space_after = Pt(0)
                run = p.add_run(src_line if src_line else " ")
                run.font.name = MONO
                run.font.size = MONO_SIZE
                run._element.rPr.rFonts.set(qn("w:eastAsia"), MONO)
            tail = doc.add_paragraph()
            tail.paragraph_format.space_after = Pt(6)
            tail.paragraph_format.line_spacing = 1.0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Генерация отчёта .docx из Markdown по ГОСТ 7.32-2017")
    ap.add_argument("source", help="исходный файл .md")
    ap.add_argument("-o", "--output", default=None, help="итоговый файл .docx")
    args = ap.parse_args()

    src = pathlib.Path(args.source).resolve()
    out = pathlib.Path(args.output).resolve() if args.output \
        else src.with_suffix(".docx")

    meta, body = split_front_matter(src.read_text(encoding="utf-8"))
    blocks = tokenize(body)
    refs = assign_numbers(blocks)

    # title_page: full (по умолчанию) | compact | none
    mode = str(meta.get("title_page", "full" if meta else "none")).lower()

    doc = Document()
    style_base(doc)
    if mode == "full" and meta:
        build_title_page(doc, meta)
    elif mode == "compact" and meta:
        build_compact_header(doc, meta)
    # section_page_break: true (все разделы), structural (только ВВЕДЕНИЕ,
    # ЗАКЛЮЧЕНИЕ и подобные), false (сплошной текст без разрывов)
    raw_break = str(meta.get("section_page_break", True)).lower()
    section_break = {"true": "all", "false": "none"}.get(raw_break, raw_break)

    render(doc, blocks, refs, src.parent,
           break_before_first=(mode == "full" and bool(meta)),
           section_break=section_break)
    add_page_numbers(doc, skip_first=(mode == "full" and bool(meta)))
    enable_update_fields(doc)
    doc.save(out)

    n_fig = sum(1 for b in blocks if b["type"] == "image")
    n_tbl = sum(1 for b in blocks if b["type"] == "table")
    n_lst = sum(1 for b in blocks if b["type"] == "code")
    print(f"Готово: {out}")
    print(f"  блоков: {len(blocks)}, рисунков: {n_fig}, "
          f"таблиц: {n_tbl}, листингов: {n_lst}")
    print("  СОДЕРЖАНИЕ обновляется в Word: Ctrl+A, затем F9 "
          "(в LibreOffice — Сервис → Обновить → Все)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
