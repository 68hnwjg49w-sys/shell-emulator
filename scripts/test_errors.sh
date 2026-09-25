#!/bin/sh
# Проверка ошибок в параметрах запуска.
# Окно не открывается: эмулятор сообщает об ошибке и завершается.
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs

echo "=== 1. Стартовый скрипт не существует ==="
./run.sh --script examples/no_such_script.txt
echo "код завершения: $?"

echo "=== 2. Вместо файла скрипта указан каталог ==="
./run.sh --script examples
echo "код завершения: $?"

echo "=== 3. Файл журнала повреждён ==="
printf 'это не xml' > logs/broken.xml
./run.sh --log logs/broken.xml
echo "код завершения: $?"

echo "=== 4. Каталог для журнала не существует ==="
./run.sh --log no/such/dir/log.xml
echo "код завершения: $?"

echo "=== 5. Вместо файла журнала указан каталог ==="
./run.sh --log logs
echo "код завершения: $?"

echo "=== 6. Журнал не в формате XML (неверное расширение) ==="
./run.sh --log logs/session.txt
echo "код завершения: $?"

echo "=== 7. Пустой путь ==="
./run.sh --log ""
echo "код завершения: $?"

echo "=== 8. Неизвестный параметр ==="
./run.sh --wat
echo "код завершения: $?"
