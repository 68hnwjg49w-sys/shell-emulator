"""Графический интерфейс эмулятора на библиотеке Tkinter.

Модуль отвечает только за ввод и вывод. Вся логика обработки
команд находится в модуле :mod:`src.shell`.
"""

import tkinter as tk
from tkinter import scrolledtext

from src.shell import CommandError, ParseError

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 560
OUTPUT_HEIGHT = 24
PROMPT_SUFFIX = "$ "


class ShellWindow:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создаёт окно и связывает его с ядром эмулятора.

        Args:
            shell: экземпляр :class:`src.shell.Shell`.
        """
        self._shell = shell
        self._root = tk.Tk()
        self._root.title("Эмулятор — VFS: {}".format(shell.vfs_name))
        self._root.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT))
        self._output = self._build_output()
        self._entry = self._build_entry()

    def _build_output(self):
        """Создаёт область вывода.

        Returns:
            Виджет прокручиваемого текстового поля.
        """
        output = scrolledtext.ScrolledText(
            self._root,
            height=OUTPUT_HEIGHT,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))
        return output

    def _build_entry(self):
        """Создаёт строку ввода с приглашением.

        Returns:
            Виджет однострочного поля ввода.
        """
        frame = tk.Frame(self._root)
        frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        prompt = self._shell.vfs_name + PROMPT_SUFFIX
        tk.Label(frame, text=prompt).pack(side=tk.LEFT)

        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._on_submit)
        entry.focus_set()
        return entry

    def _on_submit(self, event):
        """Обрабатывает нажатие Enter в строке ввода.

        Args:
            event: событие Tkinter; не используется.
        """
        del event
        line = self._entry.get()
        self._entry.delete(0, tk.END)
        self.run_line(line)

    def run_line(self, line):
        """Выполняет строку и выводит приглашение, ввод и ответ.

        Args:
            line: строка, введённая пользователем или взятая
                из стартового скрипта.
        """
        prompt = self._shell.vfs_name + PROMPT_SUFFIX
        self._write(prompt + line)
        try:
            answer = self._shell.execute(line)
        except (ParseError, CommandError) as error:
            self._write("ошибка: {}".format(error))
            return
        if answer:
            self._write(answer)
        if not self._shell.running:
            self._root.after_idle(self._root.destroy)

    def _write(self, text):
        """Добавляет строку в область вывода.

        Args:
            text: текст без завершающего перевода строки.
        """
        self._output.configure(state=tk.NORMAL)
        self._output.insert(tk.END, text + "\n")
        self._output.see(tk.END)
        self._output.configure(state=tk.DISABLED)

    def start(self):
        """Запускает цикл обработки событий Tkinter."""
        self._root.mainloop()
