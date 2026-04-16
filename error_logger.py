import tkinter as tk
from tkinter import ttk
from datetime import datetime
import logging

class ErrorLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, parent_frame: tk.Widget) -> None:
        if self._initialized:
            return
        self._initialized = True

        label = ttk.Label(parent_frame, text="Лог ошибок", font=('', 10, 'bold'))
        label.pack(anchor='w', padx=15, pady=(10, 0))

        frame = tk.Frame(parent_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ('timestamp', 'error', 'data')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', height=6)
        self.tree.heading('timestamp', text='Время')
        self.tree.heading('error', text='Ошибка')
        self.tree.heading('data', text='Введённые данные')
        self.tree.column('timestamp', width=140, anchor='center')
        self.tree.column('error', width=280, anchor='w')
        self.tree.column('data', width=250, anchor='w')
        self.tree.pack(fill=tk.BOTH, expand=True)

    def log_error(self, error_message: str, data: dict = None) -> None:

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if data:
            data_str = ', '.join(f"{k}={v}" for k, v in data.items() if v is not None)
        else:
            data_str = "—"

        if self._initialized and hasattr(self, 'tree'):
            self.tree.insert('', 0, values=(timestamp, error_message, data_str))

        log_message = f"Ошибка: {error_message} | Инф: {data_str}"
        logging.warning(log_message) 