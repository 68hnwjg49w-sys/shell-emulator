#!/bin/sh
# Проверка каждого параметра командной строки по отдельности.
# Каждый запуск открывает окно; закройте его или введите exit.
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
rm -f logs/each_param.xml

echo "=== 1. Только --vfs: имя VFS в заголовке окна — demo ==="
./run.sh --vfs images/demo.zip

echo "=== 2. Только --log: команды пишутся в logs/each_param.xml ==="
./run.sh --log logs/each_param.xml
echo "--- содержимое журнала ---"
cat logs/each_param.xml

echo "=== 3. Только --script: ошибочные строки пропускаются ==="
./run.sh --script examples/start_errors.txt
