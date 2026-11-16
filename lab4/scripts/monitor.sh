#!/bin/zsh
# Каждые 15 секунд пишет память процесса API и число сессий в CSV (данные из /metrics)
port=$1; out=$2; secs=${3:-1900}
echo "t,rss_mb,heap_mb,sessions" > $out
start=$(date +%s)
while (( $(date +%s) - start < secs )); do
  m=$(curl -s -m 5 localhost:$port/metrics)
  python3 -c "import json,sys; m=json.loads(sys.argv[1]); print(f\"{int(sys.argv[2])},{m['rss']/2**20:.1f},{m['heapUsed']/2**20:.1f},{m['sessions']}\")" "$m" $(( $(date +%s) - start )) >> $out 2>/dev/null || echo "$(( $(date +%s) - start )),,,DOWN" >> $out
  sleep 15
done
