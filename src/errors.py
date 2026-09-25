"""Исключения эмулятора, о которых нужно сообщить пользователю."""


class EmulatorError(Exception):
    """Базовая ошибка эмулятора, понятная пользователю."""


class ParseError(EmulatorError):
    """Ошибка разбора строки ввода."""


class CommandError(EmulatorError):
    """Ошибка выполнения команды."""


class ConfigError(EmulatorError):
    """Ошибка в параметрах запуска или связанных с ними файлах."""
