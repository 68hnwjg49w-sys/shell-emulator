"""Модульные тесты XML-журнала."""

import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from src.errors import ConfigError
from src.logger import STATUS_ERROR, STATUS_OK, XmlLogger

USER = "student"
MOMENT = datetime(2026, 9, 24, 12, 30, 5)
MOMENT_TEXT = "2026-09-24T12:30:05"


def fixed_clock():
    """Возвращает постоянный момент времени для тестов."""
    return MOMENT


class XmlLoggerTest(unittest.TestCase):
    """Проверяет запись событий в XML-файл."""

    def setUp(self):
        """Создаёт временный каталог и путь к журналу."""
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "log.xml"

    def tearDown(self):
        """Удаляет временный каталог."""
        self._tmp.cleanup()

    def _logger(self):
        """Создаёт журнал с постоянными пользователем и временем."""
        return XmlLogger(self.path, user=USER, clock=fixed_clock)

    def _events(self):
        """Читает события из файла журнала."""
        return ET.parse(self.path).getroot().findall("event")

    def test_creates_empty_log(self):
        """При открытии создаётся пустой журнал."""
        self._logger()
        self.assertEqual(ET.parse(self.path).getroot().tag, "log")
        self.assertEqual(self._events(), [])

    def test_successful_event(self):
        """Успешное событие содержит пользователя, время и команду."""
        self._logger().record('cd "a b" x', ["cd", "a b", "x"])
        event = self._events()[0]
        self.assertEqual(event.findtext("user"), USER)
        self.assertEqual(event.findtext("datetime"), MOMENT_TEXT)
        self.assertEqual(event.findtext("input"), 'cd "a b" x')
        self.assertEqual(event.findtext("command"), "cd")
        args = [arg.text for arg in event.findall("arg")]
        self.assertEqual(args, ["a b", "x"])
        self.assertEqual(event.findtext("status"), STATUS_OK)

    def test_error_event(self):
        """Событие с ошибкой содержит статус и сообщение."""
        self._logger().record("wat", ["wat"], "wat: команда не найдена")
        event = self._events()[0]
        self.assertEqual(event.findtext("status"), STATUS_ERROR)
        self.assertEqual(event.findtext("message"), "wat: команда не найдена")

    def test_appends_to_existing_log(self):
        """Повторное открытие дописывает события в конец."""
        self._logger().record("ls", ["ls"])
        self._logger().record("exit", ["exit"])
        commands = [event.findtext("command") for event in self._events()]
        self.assertEqual(commands, ["ls", "exit"])

    def test_invalid_xml_is_rejected(self):
        """Повреждённый файл журнала — ошибка параметров."""
        self.path.write_text("это не xml", encoding="utf-8")
        with self.assertRaises(ConfigError):
            self._logger()

    def test_foreign_xml_is_rejected(self):
        """XML-файл с чужим корневым элементом не перезаписывается."""
        self.path.write_text("<config/>", encoding="utf-8")
        with self.assertRaises(ConfigError):
            self._logger()
        self.assertEqual(self.path.read_text(encoding="utf-8"), "<config/>")

    def test_directory_instead_of_file_is_rejected(self):
        """Каталог вместо файла журнала — ошибка параметров."""
        self.path = Path(self._tmp.name)
        with self.assertRaisesRegex(ConfigError, "каталог, а не файл"):
            self._logger()

    def test_wrong_extension_is_rejected(self):
        """Журнал должен быть файлом с расширением .xml."""
        self.path = Path(self._tmp.name) / "log.txt"
        with self.assertRaisesRegex(ConfigError, "расширением .xml"):
            self._logger()
        self.assertFalse(self.path.exists())

    def test_extension_case_is_ignored(self):
        """Расширение .XML в верхнем регистре допустимо."""
        self.path = Path(self._tmp.name) / "LOG.XML"
        self._logger()
        self.assertTrue(self.path.exists())

    def test_missing_directory_is_rejected(self):
        """Журнал в несуществующем каталоге — ошибка параметров."""
        self.path = Path(self._tmp.name) / "no" / "such" / "log.xml"
        with self.assertRaisesRegex(ConfigError, "не существует"):
            self._logger()


if __name__ == "__main__":
    unittest.main()
