import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

def parse_line(line):
    parts = []
    current = ""
    in_quotes = False
    
    for char in line:
        if char == '"':
            in_quotes = not in_quotes
            current += char
        elif char == ' ' and not in_quotes:
            if current:
                parts.append(current)
                current = ""
        else:
            current += char
    if current:
        parts.append(current)
    
    planet = {'radius': None, 'type': None, 'name': '', 'date': ''}
    
    for part in parts:
        if part.startswith('"') and part.endswith('"'):
            planet['name'] = part.strip('"')
        
        elif part.isalpha():
            planet['type'] = part
        
        elif '.' in part:
            dots = part.count('.')
            if dots == 2:  
                planet['date'] = part
            elif dots == 1:  
                planet['radius'] = float(part)
    
    return planet

def read_file(filename):
    planets = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    planet = parse_line(line)
                    if planet['name']: 
                        planets.append(planet)

    except FileNotFoundError:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('3389.5 planeta "Марс" 1877.08.12\n')
            f.write('69911.0 planeta "Юпитер" 1610.01.07\n')
            f.write('6051.8 planeta "Венера" 1620.01.01\n')
            f.write('6371.0 planeta "Земля" 1600.01.01\n')
        return read_file(filename)
    
    return planets

def save_file(filename, planets):
    with open(filename, 'w', encoding='utf-8') as f:
        for p in planets:
            f.write(f'{p["radius"]} {p["type"]} "{p["name"]}" {p["date"]}\n')

class PlanetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Список планет")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.filename = "planets.txt"
        self.planets = read_file(self.filename)
        self.filtered_planets = self.planets.copy()

        self.create_table()
        self.create_buttons()
        self.update_table()
        self.create_filter_window()
    
    def create_table(self):
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

    
    def create_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        btn_add = tk.Button(frame, text="[ Добавить планету ]", 
                           command=self.add_planet)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_del = tk.Button(frame, text="[ Удалить выбранную ]", 
                           command=self.delete_planet)
        btn_del.pack(side=tk.LEFT, padx=5)
    
    def create_filter_window(self):
        self.filter_window = tk.Toplevel(self.root)
        self.filter_window.title("Фильтр планет")
        self.filter_window.geometry("250x100")
        self.filter_window.resizable(False, False)
        
        label = tk.Label(self.filter_window, text="Введите подстроку для поиска:", 
                        font=("Arial", 10))
        label.pack(pady=5)
        
        self.filter_entry = tk.Entry(self.filter_window, width=25)
        self.filter_entry.pack(pady=5)
        

        btn_apply = tk.Button(self.filter_window, text="Применить фильтр", 
                             command=self.apply_filter)
        btn_apply.pack(pady=5)
    
    def apply_filter(self):
        filter_text = self.filter_entry.get().strip().lower()
        
        if not filter_text: 
            self.filtered_planets = self.planets.copy()
        else:
            self.filtered_planets = []
            
            for planet in self.planets:
                all_fields = f"{planet['name']} {planet['type']} {planet['radius']} {planet['date']}"
                all_fields = all_fields.lower()                 
                if filter_text in all_fields:
                    self.filtered_planets.append(planet)
        
        self.update_table()
    
    def update_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        
        for p in self.filtered_planets:
            self.table.insert('', tk.END, values=(
                p['name'],
                p['type'],
                p['radius'],
                p['date']
            ))
    
    def add_planet(self):
        name = simpledialog.askstring("Добавление", "Название:")
        if not name:
            return
        
        type_obj = simpledialog.askstring("Добавление", "Тип:", initialvalue="planeta")
        if not type_obj:
            type_obj = "planeta"
        
        try:
            radius = float(simpledialog.askstring("Добавление", "Радиус (км):"))
        except:
            messagebox.showerror("Ошибка", "Нужно ввести число!")
            return
        
        date = simpledialog.askstring("Добавление", "Дата открытия (ГГГГ.ММ.ДД):")
        if not date:
            messagebox.showerror("Ошибка", "Нужно ввести дату!")
            return
        if date.count('.') != 2:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ.ММ.ДД")
            return
        
        new_planet = {
            'name': name,
            'type': type_obj,
            'radius': radius,
            'date': date
        }
        
        self.planets.append(new_planet)
        save_file(self.filename, self.planets)
        self.apply_filter()
    
    def delete_planet(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("", "Выберите планету!")
            return
       
        filtered_index = self.table.index(selected[0])
        
        planet_to_delete = self.filtered_planets[filtered_index]
        
        main_index = None
        for i, p in enumerate(self.planets):
            if (p['name'] == planet_to_delete['name'] and 
                p['date'] == planet_to_delete['date'] and
                p['radius'] == planet_to_delete['radius']):
                main_index = i
                break
        
        if main_index is not None:
            del self.planets[main_index]
            save_file(self.filename, self.planets)
            self.apply_filter()
        else:
            messagebox.showerror("Ошибка", "Не удалось найти планету в основном списке!")


if __name__ == "__main__":
    window = tk.Tk()
    app = PlanetApp(window)
    window.mainloop()