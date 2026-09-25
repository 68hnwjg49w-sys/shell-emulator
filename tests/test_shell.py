"""Модульные тесты ядра эмулятора."""

import unittest

from src.config import Config
from src.errors import CommandError, ParseError
from src.shell import Shell, tokenize

VFS_PATH = "images/testvfs.zip"
VFS_NAME = "testvfs"


class FakeLogger:
    """Журнал-заглушка, запоминающий события в памяти."""

    def __init__(self):
        """Создаёт пустой список событий."""
        self.events = []

    def record(self, line, tokens, error=None):
        """Запоминает событие."""
        self.events.append((line, list(tokens), error))


class TokenizeTest(unittest.TestCase):
    """Проверяет разбор строки ввода на токены."""

    def test_empty_line(self):
        """Пустая строка не содержит токенов."""
        self.assertEqual(tokenize(""), [])

    def test_only_spaces(self):
        """Строка из пробелов не содержит токенов."""
        self.assertEqual(tokenize("   "), [])

    def test_single_command(self):
        """Команда без аргументов даёт один токен."""
        self.assertEqual(tokenize("ls"), ["ls"])

    def test_command_with_arguments(self):
        """Аргументы отделяются пробелами."""
        self.assertEqual(tokenize("ls -la /tmp"), ["ls", "-la", "/tmp"])

    def test_repeated_spaces(self):
        """Несколько пробелов подряд считаются одним разделителем."""
        self.assertEqual(tokenize("ls     -la"), ["ls", "-la"])

    def test_quoted_argument(self):
        """Кавычки сохраняют пробел внутри аргумента."""
        self.assertEqual(tokenize('cd "my folder"'), ["cd", "my folder"])

    def test_empty_quoted_argument(self):
        """Пустые кавычки дают пустой, но существующий аргумент."""
        self.assertEqual(tokenize('cd ""'), ["cd", ""])

    def test_quotes_inside_word(self):
        """Кавычки могут стоять в середине слова."""
        self.assertEqual(tokenize('echo a"b c"d'), ["echo", "ab cd"])

    def test_unclosed_quote(self):
        """Незакрытая кавычка приводит к ошибке разбора."""
        with self.assertRaises(ParseError):
            tokenize('cd "не закрыл')


class ShellTest(unittest.TestCase):
    """Проверяет выполнение команд ядром эмулятора."""

    def setUp(self):
        """Создаёт новое ядро перед каждым тестом."""
        self.config = Config(vfs_path=VFS_PATH)
        self.shell = Shell(self.config)

    def test_vfs_name_from_path(self):
        """Имя VFS берётся из имени файла без расширения."""
        self.assertEqual(self.shell.vfs_name, VFS_NAME)

    def test_blank_line_gives_no_answer(self):
        """Пустой ввод не порождает ответа."""
        self.assertEqual(self.shell.execute("   "), "")

    def test_stub_without_arguments(self):
        """Заглушка сообщает об отсутствии аргументов."""
        self.assertEqual(self.shell.execute("ls"), "ls: аргументов нет")

    def test_stub_reports_arguments(self):
        """Заглушка выводит своё имя и аргументы."""
        answer = self.shell.execute('cd "my folder" -x')
        self.assertEqual(answer, "cd: аргументы: 'my folder', '-x'")

    def test_unknown_command(self):
        """Неизвестная команда приводит к ошибке."""
        with self.assertRaises(CommandError):
            self.shell.execute("wat")

    def test_exit_stops_shell(self):
        """Команда exit снимает признак работы."""
        self.shell.execute("exit")
        self.assertFalse(self.shell.running)

    def test_exit_rejects_arguments(self):
        """Команда exit не принимает аргументов."""
        with self.assertRaises(CommandError):
            self.shell.execute("exit now")
        self.assertTrue(self.shell.running)

    def test_conf_dump(self):
        """Команда conf-dump выводит параметры в формате ключ-значение."""
        self.assertEqual(self.shell.execute("conf-dump"), self.config.dump())

    def test_conf_dump_rejects_arguments(self):
        """Команда conf-dump не принимает аргументов."""
        with self.assertRaises(CommandError):
            self.shell.execute("conf-dump extra")


class ShellLoggingTest(unittest.TestCase):
    """Проверяет передачу событий в журнал."""

    def setUp(self):
        """Создаёт ядро с журналом-заглушкой."""
        self.logger = FakeLogger()
        self.shell = Shell(Config(), self.logger)

    def test_successful_call_is_logged(self):
        """Успешный вызов записывается без ошибки."""
        self.shell.execute('ls "a b"')
        expected = [('ls "a b"', ["ls", "a b"], None)]
        self.assertEqual(self.logger.events, expected)

    def test_failed_command_is_logged(self):
        """Вызов неизвестной команды записывается с текстом ошибки."""
        with self.assertRaises(CommandError):
            self.shell.execute("wat 1")
        line, tokens, error = self.logger.events[0]
        self.assertEqual((line, tokens), ("wat 1", ["wat", "1"]))
        self.assertIn("не найдена", error)

    def test_parse_error_is_logged(self):
        """Ошибка разбора записывается без токенов."""
        with self.assertRaises(ParseError):
            self.shell.execute('cd "x')
        self.assertEqual(self.logger.events[0][1], [])

    def test_blank_line_is_not_logged(self):
        """Пустой ввод не является вызовом команды."""
        self.shell.execute("  ")
        self.assertEqual(self.logger.events, [])


if __name__ == "__main__":
    unittest.main()
