"""Ядро эмулятора командной оболочки.

Модуль не зависит от способа ввода-вывода: он принимает строку
и возвращает текст ответа. Благодаря этому ядро можно покрыть
модульными тестами без запуска графического интерфейса.
"""

QUOTE_CHAR = '"'


class ParseError(Exception):
    """Ошибка разбора строки ввода."""


class CommandError(Exception):
    """Ошибка выполнения команды."""


def tokenize(line):
    """Разбивает строку ввода на команду и аргументы.

    Двойные кавычки группируют текст: пробелы внутри кавычек не
    разделяют слова. Сами кавычки являются управляющими символами
    и в результат не попадают.

    Args:
        line: строка, введённая пользователем.

    Returns:
        Список токенов. Первый элемент — имя команды, остальные —
        её аргументы. Для пустой строки возвращается пустой список.

    Raises:
        ParseError: если кавычка открыта, но не закрыта.
    """
    tokens = []
    current = []
    has_token = False
    in_quotes = False

    for char in line:
        if char == QUOTE_CHAR:
            in_quotes = not in_quotes
            has_token = True
        elif char.isspace() and not in_quotes:
            if has_token:
                tokens.append("".join(current))
                current = []
                has_token = False
        else:
            current.append(char)
            has_token = True

    if in_quotes:
        raise ParseError("незакрытая кавычка в строке ввода")
    if has_token:
        tokens.append("".join(current))
    return tokens


class Shell:
    """Ядро эмулятора: хранит состояние и выполняет команды."""

    def __init__(self, vfs_name):
        """Создаёт ядро эмулятора.

        Args:
            vfs_name: имя виртуальной файловой системы.
        """
        self.vfs_name = vfs_name
        self.running = True
        self._commands = {
            "ls": self._stub,
            "cd": self._stub,
            "exit": self._exit,
        }

    def execute(self, line):
        """Выполняет одну строку ввода.

        Args:
            line: строка, введённая пользователем.

        Returns:
            Текст ответа эмулятора. Пустая строка, если вводить
            было нечего.

        Raises:
            ParseError: если строка разобрана некорректно.
            CommandError: если команда неизвестна или вызвана неверно.
        """
        tokens = tokenize(line)
        if not tokens:
            return ""

        name = tokens[0]
        args = tokens[1:]
        handler = self._commands.get(name)
        if handler is None:
            raise CommandError("{}: команда не найдена".format(name))
        return handler(name, args)

    @staticmethod
    def _stub(name, args):
        """Заглушка команды: выводит своё имя и аргументы.

        Args:
            name: имя вызванной команды.
            args: список её аргументов.

        Returns:
            Строку с именем команды и перечнем аргументов.
        """
        if not args:
            return "{}: аргументов нет".format(name)
        listed = ", ".join(repr(arg) for arg in args)
        return "{}: аргументы: {}".format(name, listed)

    def _exit(self, name, args):
        """Завершает работу эмулятора.

        Args:
            name: имя вызванной команды.
            args: список её аргументов; должен быть пустым.

        Returns:
            Прощальное сообщение.

        Raises:
            CommandError: если команде переданы аргументы.
        """
        if args:
            raise CommandError("{}: аргументы не поддерживаются".format(name))
        self.running = False
        return "Завершение работы эмулятора."
