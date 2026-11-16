#!/bin/zsh
# Сборка отчетов: Markdown -> DOCX (ГОСТ) -> PDF
set -e
cd "$(dirname "$0")"
mkdir -p out
for n in ${@:-1 2 3 4 5}; do
  python3 md2docx.py lab$n.md -o "out/Отчёт_ЛР${n}_Управление_качеством.docx" | head -2
  (cd out && soffice --headless --convert-to pdf "Отчёт_ЛР${n}_Управление_качеством.docx" >/dev/null 2>&1)
done
