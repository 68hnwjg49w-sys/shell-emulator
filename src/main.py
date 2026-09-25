"""Точка входа эмулятора командной оболочки."""

import sys

from src.config import parse_arguments, read_script
from src.errors import ConfigError
from src.gui import ShellWindow
from src.logger import XmlLogger
from src.shell import Shell

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
DEBUG_PREFIX = "[debug] "


def print_debug(config):
    """Выводит в терминал все параметры запуска эмулятора."""
    print(DEBUG_PREFIX + "параметры запуска эмулятора:")
    for line in config.dump().splitlines():
        print(DEBUG_PREFIX + "  " + line)


def prepare(config):
    """Читает стартовый скрипт и открывает журнал, если они заданы."""
    script = read_script(config.script_path) if config.script_path else []
    logger = XmlLogger(config.log_path) if config.log_path else None
    return script, logger


def main(argv=None):
    """Запускает эмулятор и возвращает код завершения процесса."""
    try:
        config = parse_arguments(argv)
        print_debug(config)
        script, logger = prepare(config)
    except ConfigError as error:
        print("ошибка запуска: {}".format(error), file=sys.stderr)
        return EXIT_CONFIG_ERROR

    window = ShellWindow(Shell(config, logger))
    window.run_script(script)
    window.start()
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
