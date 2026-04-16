import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging

from planet_model import PlanetModel, PlanetValidationError
from error_logger import ErrorLogger

logger = logging.getLogger(__name__)


class PlanetApp:
    def __init__(self, root: tk.Tk, model: PlanetModel):
        self.root = root
        self.model = model

        self.root.title("Список планет")
        self.root.geometry("700x550")
        self.root.resizable(False, False)

        self.error_logger = ErrorLogger()
        self._create_table()
        self._create_buttons()

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.error_logger.initialize(bottom_frame)

        self._refresh_table()

    def _create_table(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(pady=8, padx=15, fill=tk.BOTH, expand=True)

        columns = ('name', 'type', 'radius', 'date')
        self.table = ttk.Treeview(frame, columns=columns, show='headings')

        self.table.heading('name', text='Название')
        self.table.heading('type', text='Тип')
        self.table.heading('radius', text='Радиус (км)')
        self.table.heading('date', text='Дата открытия')

        self.table.column('name', width=130, anchor='center')
        self.table.column('type', width=80, anchor='center')
        self.table.column('radius', width=100, anchor='center')
        self.table.column('date', width=130, anchor='center')

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _create_buttons(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="[ Добавить планету ]",
                  command=self._on_add).pack(side=tk.LEFT, padx=5)

        tk.Button(frame, text="[ Удалить выбранную ]",
                  command=self._on_delete).pack(side=tk.LEFT, padx=5)

    def _refresh_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)

        for planet in self.model.get_all():
            self.table.insert('', tk.END, values=(
                planet.name,
                planet.planet_type,
                planet.radius,
                planet.date
            ))

    def _on_add(self) -> None:
        name = simpledialog.askstring("Добавление", "Название:")
        if name is None:
            return

        planet_type = simpledialog.askstring("Добавление", "Тип:", initialvalue="planeta")
        if planet_type is None:
            return

        radius_str = simpledialog.askstring("Добавление", "Радиус (км):")
        if radius_str is None:
            return

        try:
            radius = float(radius_str)
        except ValueError:
            error_msg = "Радиус должен быть числом!"
            messagebox.showerror("Ошибка", error_msg)
            self.error_logger.log_error(
                error_msg,
                {'name': name, 'type': planet_type, 'radius': radius_str, 'date': None}
            )
            return

        date = simpledialog.askstring("Добавление", "Дата открытия (ГГГГ.ММ.ДД):")
        if date is None:
            return

        try:
            self.model.add_planet(name, planet_type, radius, date)
            self._refresh_table()
        except PlanetValidationError as e:
            error_msg = str(e)
            messagebox.showerror("Ошибка валидации", error_msg)
            self.error_logger.log_error(
                error_msg,
                {'name': name, 'type': planet_type, 'radius': radius, 'date': date}
            )

    def _on_delete(self) -> None:
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("", "Выберите планету!")
            return

        index = self.table.index(selected[0])
        self.model.delete_planet(index)
        self._refresh_table()


if __name__ == "__main__":
    model = PlanetModel("planets.txt")
    window = tk.Tk()
    app = PlanetApp(window, model)
    window.mainloop()