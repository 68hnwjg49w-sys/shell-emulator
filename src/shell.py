"""Ядро эмулятора: разбор строки и выполнение команд без привязки к GUI."""

from src.errors import CommandError, ParseError

QUOTE_CHAR = '"'


def tokenize(line):
    """Разбивает строку на команду и аргументы с учётом кавычек."""
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

    def __init__(self, config, logger=None):
        """Создаёт ядро с параметрами запуска и необязательным журналом."""
        self.config = config
        self.vfs_name = config.vfs_name
        self.running = True
        self._logger = logger
        self._commands = {
            "ls": self._stub,
            "cd": self._stub,
            "exit": self._exit,
            "conf-dump": self._conf_dump,
        }

    def execute(self, line):
        """Выполняет строку, пишет событие в журнал и возвращает ответ."""
        if not line.strip():
            return ""
        tokens = []
        try:
            tokens = tokenize(line)
            answer = self._dispatch(tokens)
        except (ParseError, CommandError) as error:
            self._record(line, tokens, str(error))
            raise
        self._record(line, tokens, None)
        return answer

    def _dispatch(self, tokens):
        """Находит обработчик команды и вызывает его."""
        name = tokens[0]
        handler = self._commands.get(name)
        if handler is None:
            raise CommandError("{}: команда не найдена".format(name))
        return handler(name, tokens[1:])

    def _record(self, line, tokens, error):
        """Передаёт событие в журнал, если он ведётся."""
        if self._logger is not None:
            self._logger.record(line, tokens, error)

    @staticmethod
    def _stub(name, args):
        """Заглушка команды: возвращает своё имя и аргументы."""
        if not args:
            return "{}: аргументов нет".format(name)
        listed = ", ".join(repr(arg) for arg in args)
        return "{}: аргументы: {}".format(name, listed)

    def _exit(self, name, args):
        """Завершает работу эмулятора."""
        _require_no_args(name, args)
        self.running = False
        return "Завершение работы эмулятора."

    def _conf_dump(self, name, args):
        """Возвращает параметры эмулятора в формате «ключ = значение»."""
        _require_no_args(name, args)
        return self.config.dump()


def _require_no_args(name, args):
    """Бросает CommandError, если команде переданы аргументы."""
    if args:
        raise CommandError("{}: аргументы не поддерживаются".format(name))
