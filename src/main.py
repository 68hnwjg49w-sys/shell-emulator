"""Точка входа эмулятора командной оболочки."""

import argparse

from src.gui import ShellWindow
from src.shell import Shell

DEFAULT_VFS_NAME = "vfs"


def parse_arguments(argv=None):
    """Разбирает параметры командной строки.

    Args:
        argv: список аргументов; по умолчанию берётся из sys.argv.

    Returns:
        Пространство имён с разобранными параметрами.
    """
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs-name",
        default=DEFAULT_VFS_NAME,
        help="имя VFS, отображаемое в заголовке окна",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Собирает ядро и интерфейс и запускает эмулятор.

    Args:
        argv: список аргументов командной строки.
    """
    arguments = parse_arguments(argv)
    shell = Shell(arguments.vfs_name)
    ShellWindow(shell).start()


if __name__ == "__main__":
    main()
