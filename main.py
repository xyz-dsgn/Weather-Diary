# weather_diary.py

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import re

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Data storage
        self.records = []
        self.data_file = "weather_data.json"
        
        # Load existing data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
        # Refresh table
        self.refresh_table()
    
    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ==================== INPUT FRAME ====================
        input_frame = ttk.LabelFrame(main_frame, text="Добавить запись о погоде", padding="10")
        input_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Date
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Temperature
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.temp_var = tk.StringVar()
        self.temp_entry = ttk.Entry(input_frame, textvariable=self.temp_var, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Description
        ttk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(input_frame, textvariable=self.desc_var, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Precipitation
        ttk.Label(input_frame, text="Осадки:").grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)
        self.precip_var = tk.BooleanVar(value=False)
        self.precip_check = ttk.Checkbutton(input_frame, text="Да", variable=self.precip_var)
        self.precip_check.grid(row=1, column=5, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        self.add_button.grid(row=2, column=0, columnspan=6, pady=10)
        
        # ==================== FILTER FRAME ====================
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Filter by date
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_var = tk.StringVar()
        self.filter_date_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Filter by temperature
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_var = tk.StringVar()
        self.filter_temp_entry = ttk.Entry(filter_frame, textvariable=self.filter_temp_var, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Filter buttons
        self.apply_filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table)
        self.apply_filter_button.grid(row=0, column=4, padx=5, pady=5)
        
        self.clear_filter_button = ttk.Button(filter_frame, text="Очистить фильтры", command=self.clear_filters)
        self.clear_filter_button.grid(row=0, column=5, padx=5, pady=5)
        
        # ==================== TABLE FRAME ====================
        table_frame = ttk.LabelFrame(main_frame, text="Записи о погоде", padding="10")
        table_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Create Treeview
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Температура", text="Температура (°C)")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Осадки", text="Осадки")
        
        # Define columns
        self.tree.column("Дата", width=120)
        self.tree.column("Температура", width=120)
        self.tree.column("Описание", width=300)
        self.tree.column("Осадки", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout for table
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # ==================== BUTTONS FRAME ====================
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        # Delete button
        self.delete_button = ttk.Button(buttons_frame, text="Удалить выбранную запись", command=self.delete_record)
        self.delete_button.grid(row=0, column=0, padx=5)
        
        # Save button
        self.save_button = ttk.Button(buttons_frame, text="Сохранить в JSON", command=self.save_data)
        self.save_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(buttons_frame, text="Загрузить из JSON", command=self.load_data)
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def validate_date(self, date_string):
        """Validate date format (YYYY-MM-DD)"""
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_string):
            return False
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_string):
        """Validate temperature (number)"""
        try:
            temp = float(temp_string)
            return True
        except ValueError:
            return False
    
    def add_record(self):
        """Add a new weather record"""
        date = self.date_var.get().strip()
        temperature = self.temp_var.get().strip()
        description = self.desc_var.get().strip()
        precipitation = self.precip_var.get()
        
        # Validate inputs
        if not date:
            messagebox.showerror("Ошибка", "Пожалуйста, введите дату")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        if not temperature:
            messagebox.showerror("Ошибка", "Пожалуйста, введите температуру")
            return
        
        if not self.validate_temperature(temperature):
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Пожалуйста, введите описание погоды")
            return
        
        # Add record
        record = {
            "date": date,
            "temperature": float(temperature),
            "description": description,
            "precipitation": precipitation
        }
        
        self.records.append(record)
        self.save_data()
        self.refresh_table()
        
        # Clear inputs
        self.date_var.set("")
        self.temp_var.set("")
        self.desc_var.set("")
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись о погоде успешно добавлена!")
    
    def delete_record(self):
        """Delete selected weather record"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите запись для удаления")
            return
        
        # Get the index of the selected item
        item = selected_item[0]
        values = self.tree.item(item, 'values')
        
        # Find and remove the record
        precip_text = "Да" if values[3] == "Да" else "Нет"
        for i, record in enumerate(self.records):
            if (record['date'] == values[0] and 
                str(record['temperature']) == values[1] and 
                record['description'] == values[2] and
                ("Да" if record['precipitation'] else "Нет") == precip_text):
                del self.records[i]
                break
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Запись удалена!")
    
    def refresh_table(self):
        """Refresh the table with current filters"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Apply filters
        filter_date = self.filter_date_var.get().strip()
        filter_temp_str = self.filter_temp_var.get().strip()
        
        filtered_records = self.records.copy()
        
        # Filter by date
        if filter_date:
            filtered_records = [r for r in filtered_records if r['date'] == filter_date]
        
        # Filter by temperature (above)
        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered_records = [r for r in filtered_records if r['temperature'] > min_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом")
                return
        
        # Sort by date
        filtered_records.sort(key=lambda x: x['date'])
        
        # Add to table
        for record in filtered_records:
            precip_text = "Да" if record['precipitation'] else "Нет"
            self.tree.insert("", tk.END, values=(
                record['date'],
                f"{record['temperature']:.1f}",
                record['description'],
                precip_text
            ))
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_date_var.set("")
        self.filter_temp_var.set("")
        self.refresh_table()
    
    def save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            return False
    
    def load_data(self):
        """Load data from JSON file"""
        if not os.path.exists(self.data_file):
            self.records = []
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
            self.refresh_table()
            messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
            self.records = []
            return False

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()