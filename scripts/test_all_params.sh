#!/bin/sh
# Проверка всех параметров вместе и дозаписи журнала.
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
rm -f logs/all_params.xml

echo "=== 1. Все параметры, демонстрационный скрипт ==="
./run.sh --vfs images/demo.zip --log logs/all_params.xml \
    --script examples/start_demo.txt

echo "=== 2. Скрипт с exit: окно закроется само, журнал дополнится ==="
./run.sh --vfs images/demo.zip --log logs/all_params.xml \
    --script examples/start_exit.txt

echo "--- содержимое журнала ---"
cat logs/all_params.xml
