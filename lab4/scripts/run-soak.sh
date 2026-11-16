#!/bin/zsh
# Запуск двух soak-тестов параллельно (с утечкой и исправленный) и мониторинга памяти
cd "$(dirname "$0")/.."
scripts/monitor.sh 8093 results/soak-leak-memory.csv 1850 &
scripts/monitor.sh 8094 results/soak-fixed-memory.csv 1850 &
BASE_URL=http://localhost:8094 k6 run --summary-export=results/soak-fixed-summary.json --out json=results/soak-fixed.json scripts/soak-test.js > results/soak-fixed-console.txt 2>&1 &
BASE_URL=http://localhost:8093 k6 run --summary-export=results/soak-leak-summary.json --out json=results/soak-leak.json scripts/soak-test.js > results/soak-leak-console.txt 2>&1
wait
