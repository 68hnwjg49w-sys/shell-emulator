"""Параметры запуска эмулятора и чтение стартового скрипта."""

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.errors import ConfigError

DEFAULT_VFS_NAME = "vfs"
NOT_SET = "(не задан)"
COMMENT_PREFIX = "#"


@dataclass(frozen=True)
class Config:
    """Параметры запуска: пути к VFS, журналу и стартовому скрипту."""

    vfs_path: str | None = None
    log_path: str | None = None
    script_path: str | None = None

    @property
    def vfs_name(self):
        """Имя VFS: имя файла без расширения или имя по умолчанию."""
        if not self.vfs_path:
            return DEFAULT_VFS_NAME
        return Path(self.vfs_path).stem or DEFAULT_VFS_NAME

    def items(self):
        """Возвращает параметры списком пар «ключ, значение»."""
        pairs = [
            ("vfs_path", self.vfs_path),
            ("vfs_name", self.vfs_name),
            ("log_path", self.log_path),
            ("script_path", self.script_path),
        ]
        return [(key, _or_not_set(value)) for key, value in pairs]

    def dump(self):
        """Возвращает параметры текстом в формате «ключ = значение»."""
        return "\n".join(
            "{} = {}".format(key, value) for key, value in self.items()
        )


def _or_not_set(value):
    """Заменяет None пометкой «не задан»."""
    return NOT_SET if value is None else value


def build_parser():
    """Создаёт разборщик параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="GUI-эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--log", dest="log_path", metavar="PATH",
        help="путь к XML-файлу журнала вызовов команд",
    )
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту",
    )
    return parser


def parse_arguments(argv=None):
    """Разбирает параметры командной строки в объект Config."""
    namespace = build_parser().parse_args(argv)
    config = Config(
        vfs_path=namespace.vfs_path,
        log_path=namespace.log_path,
        script_path=namespace.script_path,
    )
    for key, value in config.items():
        if value == "":
            raise ConfigError("параметр {} задан пустым".format(key))
    return config


def read_script(path):
    """Читает стартовый скрипт без пустых строк и комментариев."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConfigError(
            "стартовый скрипт не найден: {}".format(path)
        ) from None
    except (OSError, UnicodeDecodeError) as error:
        raise ConfigError(
            "не удалось прочитать стартовый скрипт {}: {}".format(path, error)
        ) from error
    return [line for line in text.splitlines() if _is_command(line)]


def _is_command(line):
    """Проверяет, что строка скрипта не пустая и не комментарий."""
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(COMMENT_PREFIX)
