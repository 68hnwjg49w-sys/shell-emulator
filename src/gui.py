"""Графический интерфейс эмулятора на Tkinter: только ввод и вывод."""

import tkinter as tk
from tkinter import scrolledtext

from src.errors import EmulatorError

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 560
OUTPUT_HEIGHT = 24
PADDING = 8
PROMPT_SUFFIX = "$ "


class ShellWindow:
    """Окно эмулятора: область вывода и строка ввода."""

    def __init__(self, shell):
        """Создаёт окно и связывает его с ядром эмулятора."""
        self._shell = shell
        self._root = tk.Tk()
        self._root.title("Эмулятор — VFS: {}".format(shell.vfs_name))
        self._root.geometry("{}x{}".format(WINDOW_WIDTH, WINDOW_HEIGHT))
        self._output = self._build_output()
        self._entry = self._build_entry()

    def _build_output(self):
        """Создаёт прокручиваемую область вывода."""
        output = scrolledtext.ScrolledText(
            self._root,
            height=OUTPUT_HEIGHT,
            state=tk.DISABLED,
            wrap=tk.WORD,
        )
        output.pack(
            fill=tk.BOTH, expand=True,
            padx=PADDING, pady=(PADDING, PADDING // 2),
        )
        return output

    def _build_entry(self):
        """Создаёт строку ввода с приглашением."""
        frame = tk.Frame(self._root)
        frame.pack(fill=tk.X, padx=PADDING, pady=(0, PADDING))

        tk.Label(frame, text=self._prompt()).pack(side=tk.LEFT)

        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self._on_submit)
        entry.focus_set()
        return entry

    def _prompt(self):
        """Возвращает текст приглашения к вводу."""
        return self._shell.vfs_name + PROMPT_SUFFIX

    def _on_submit(self, event):
        """Обрабатывает нажатие Enter в строке ввода."""
        del event
        line = self._entry.get()
        self._entry.delete(0, tk.END)
        self.run_line(line)

    def run_line(self, line):
        """Выполняет строку и выводит приглашение, ввод и ответ.

        Ошибки ввода выводятся в окно и не прерывают работу.
        """
        self._write(self._prompt() + line)
        try:
            answer = self._shell.execute(line)
        except EmulatorError as error:
            self._write("ошибка: {}".format(error))
            return
        if answer:
            self._write(answer)
        if not self._shell.running:
            self._entry.configure(state=tk.DISABLED)
            self._root.after_idle(self._root.destroy)

    def run_script(self, lines):
        """Выполняет команды стартового скрипта до конца или до exit."""
        for line in lines:
            if not self._shell.running:
                return
            self.run_line(line)

    def _write(self, text):
        """Добавляет строку текста в область вывода."""
        self._output.configure(state=tk.NORMAL)
        self._output.insert(tk.END, text + "\n")
        self._output.see(tk.END)
        self._output.configure(state=tk.DISABLED)

    def start(self):
        """Запускает цикл обработки событий Tkinter."""
        self._root.mainloop()
