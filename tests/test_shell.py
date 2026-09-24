"""Модульные тесты ядра эмулятора."""

import unittest

from src.shell import CommandError, ParseError, Shell, tokenize

VFS_NAME = "testvfs"


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
        self.shell = Shell(VFS_NAME)

    def test_vfs_name_is_stored(self):
        """Ядро запоминает имя VFS."""
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


if __name__ == "__main__":
    unittest.main()
