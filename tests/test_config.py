"""Модульные тесты параметров запуска."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from src.config import (
    DEFAULT_VFS_NAME, NOT_SET, Config, parse_arguments, read_script,
)
from src.errors import ConfigError


class ParseArgumentsTest(unittest.TestCase):
    """Проверяет разбор параметров командной строки."""

    def test_no_arguments(self):
        """Без параметров все пути не заданы."""
        self.assertEqual(parse_arguments([]), Config())

    def test_all_arguments(self):
        """Все три параметра разбираются в соответствующие поля."""
        config = parse_arguments(
            ["--vfs", "a.zip", "--log", "b.xml", "--script", "c.txt"]
        )
        self.assertEqual(config, Config("a.zip", "b.xml", "c.txt"))

    def test_empty_path_is_rejected(self):
        """Пустой путь считается ошибкой параметров."""
        with self.assertRaises(ConfigError):
            parse_arguments(["--log", ""])

    def test_unknown_argument_is_rejected(self):
        """Неизвестный параметр завершает разбор с ошибкой."""
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            parse_arguments(["--wat"])


class ConfigTest(unittest.TestCase):
    """Проверяет хранение и вывод параметров."""

    def test_default_vfs_name(self):
        """Без пути к VFS используется имя по умолчанию."""
        self.assertEqual(Config().vfs_name, DEFAULT_VFS_NAME)

    def test_vfs_name_from_path(self):
        """Имя VFS — имя файла без расширения."""
        self.assertEqual(Config("images/demo.zip").vfs_name, "demo")

    def test_dump_format(self):
        """Параметры выводятся в формате «ключ = значение»."""
        dump = Config(vfs_path="x.zip", log_path="log.xml").dump()
        self.assertEqual(dump.splitlines(), [
            "vfs_path = x.zip",
            "vfs_name = x",
            "log_path = log.xml",
            "script_path = " + NOT_SET,
        ])


class ReadScriptTest(unittest.TestCase):
    """Проверяет чтение стартового скрипта."""

    def setUp(self):
        """Создаёт временный каталог."""
        self._tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self._tmp.name)

    def tearDown(self):
        """Удаляет временный каталог."""
        self._tmp.cleanup()

    def test_skips_comments_and_blank_lines(self):
        """Комментарии и пустые строки не считаются командами."""
        path = self.directory / "start.txt"
        path.write_text("# comment\n\nls\n   \ncd x\n", encoding="utf-8")
        self.assertEqual(read_script(path), ["ls", "cd x"])

    def test_missing_file(self):
        """Отсутствующий файл скрипта — ошибка параметров."""
        with self.assertRaises(ConfigError):
            read_script(self.directory / "missing.txt")

    def test_directory_instead_of_file(self):
        """Каталог вместо файла — ошибка параметров."""
        with self.assertRaises(ConfigError):
            read_script(self.directory)


if __name__ == "__main__":
    unittest.main()
