"""Журнал вызовов команд в формате XML с дозаписью в существующий файл."""

import getpass
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from src.errors import ConfigError

ROOT_TAG = "log"
EVENT_TAG = "event"
XML_INDENT = "  "
STATUS_OK = "ok"
STATUS_ERROR = "error"
UNKNOWN_USER = "unknown"
LOG_SUFFIX = ".xml"


def current_user():
    """Возвращает имя пользователя ОС или «unknown»."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return UNKNOWN_USER


def check_log_path(path):
    """Проверяет, что путь ведёт к XML-файлу в существующем каталоге."""
    if path.is_dir():
        raise ConfigError(
            "журнал {}: указан каталог, а не файл".format(path)
        )
    if path.suffix.lower() != LOG_SUFFIX:
        raise ConfigError(
            "журнал {}: нужен файл с расширением {}".format(path, LOG_SUFFIX)
        )
    if not path.parent.is_dir():
        raise ConfigError(
            "журнал {}: каталог {} не существует".format(path, path.parent)
        )


class XmlLogger:
    """Записывает события вызова команд в XML-файл."""

    def __init__(self, path, user=None, clock=datetime.now):
        """Открывает журнал и сразу проверяет, что в него можно писать."""
        self.path = Path(path)
        check_log_path(self.path)
        self.user = user if user is not None else current_user()
        self._clock = clock
        self._root = self._load()
        self._save()

    def record(self, line, tokens, error=None):
        """Записывает в журнал событие вызова команды."""
        event = ET.SubElement(self._root, EVENT_TAG)
        moment = self._clock().isoformat(timespec="seconds")
        _add_child(event, "user", self.user)
        _add_child(event, "datetime", moment)
        _add_child(event, "input", line)
        if tokens:
            _add_child(event, "command", tokens[0])
            for argument in tokens[1:]:
                _add_child(event, "arg", argument)
        _add_child(event, "status", STATUS_ERROR if error else STATUS_OK)
        if error:
            _add_child(event, "message", error)
        self._save()

    def _load(self):
        """Загружает существующий журнал или создаёт пустой."""
        if not self.path.exists():
            return ET.Element(ROOT_TAG)
        try:
            root = ET.parse(self.path).getroot()
        except (ET.ParseError, OSError) as error:
            raise ConfigError(
                "журнал {} повреждён: {}".format(self.path, error)
            ) from error
        if root.tag != ROOT_TAG:
            raise ConfigError(
                "журнал {}: ожидался корневой элемент <{}>, найден <{}>"
                .format(self.path, ROOT_TAG, root.tag)
            )
        return root

    def _save(self):
        """Сохраняет журнал на диск."""
        tree = ET.ElementTree(self._root)
        ET.indent(tree, space=XML_INDENT)
        try:
            tree.write(self.path, encoding="utf-8", xml_declaration=True)
        except OSError as error:
            raise ConfigError(
                "не удалось записать журнал {}: {}".format(self.path, error)
            ) from error


def _add_child(parent, tag, text):
    """Добавляет дочерний элемент с текстом."""
    ET.SubElement(parent, tag).text = text
