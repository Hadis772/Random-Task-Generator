import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

# ---------------------------- Data Handling ----------------------------
class TaskManager:
    def __init__(self):
        self.predefined_tasks = [
            {"name": "Прочитать статью о Python", "type": "учеба"},
            {"name": "Сделать 10 мин зарядки", "type": "спорт"},
            {"name": "Написать еженедельный отчёт", "type": "работа"},
            {"name": "Изучить новый алгоритм", "type": "учеба"},
            {"name": "Пробежка на 2 км", "type": "спорт"},
            {"name": "Позвонить клиенту", "type": "работа"},
            {"name": "Посмотреть вебинар", "type": "учеба"},
            {"name": "Отжимания 20 раз", "type": "спорт"},
            {"name": "Планирование задач на неделю", "type": "работа"}
        ]
        self.tasks_file = "tasks.json"
        self.history_file = "history.json"
        self.tasks = []          # all available tasks (predefined + user added)
        self.history = []        # list of generated tasks (with timestamp)
        self.load_tasks()
        self.load_history()

    def load_tasks(self):
        """Load tasks from JSON file; if missing, use predefined tasks."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = self.predefined_tasks.copy()
        else:
            self.tasks = self.predefined_tasks.copy()
            self.save_tasks()

    def save_tasks(self):
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def add_task(self, name, task_type):
        """Add a new task to the pool (validation: non‑empty)."""
        if not name.strip():
            return False
        new_task = {"name": name.strip(), "type": task_type}
        self.tasks.append(new_task)
        self.save_tasks()
        return True

    def generate_random_task(self):
        """Return a random task dict from the current pool."""
        if not self.tasks:
            return None
        return random.choice(self.tasks)

    def add_to_history(self, task):
        """Append a generated task with timestamp to history and save."""
        entry = {
            "name": task["name"],
            "type": task["type"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.save_history()

    def get_filtered_history(self, filter_type):
        """Return history entries filtered by type (or all if 'Все')."""
        if filter_type == "Все":
            return self.history
        return [h for h in self.history if h["type"] == filter_type]

# ---------------------------- GUI Application ----------------------------
class RandomTaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        self.manager = TaskManager()
        self.current_filter = tk.StringVar(value="Все")

        self._setup_ui()
        self._refresh_history_display()

    def _setup_ui(self):
        # ---------- Generation frame ----------
        gen_frame = ttk.LabelFrame(self.root, text="Генератор задач", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        self.generate_btn = ttk.Button(gen_frame, text="Сгенерировать задачу", command=self.generate_task)
        self.generate_btn.pack(pady=5)

        self.current_task_label = ttk.Label(gen_frame, text="", font=("Arial", 12, "bold"), foreground="green")
        self.current_task_label.pack(pady=5)

        # ---------- History frame with filter ----------
        hist_frame = ttk.LabelFrame(self.root, text="История задач", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        filter_frame = ttk.Frame(hist_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Фильтр по типу:").pack(side="left", padx=5)
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.current_filter,
                                    values=["Все", "учеба", "спорт", "работа"], state="readonly")
        filter_combo.pack(side="left", padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_history_display())

        # History listbox + scrollbar
        list_frame = ttk.Frame(hist_frame)
        list_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(list_frame, height=12, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---------- Add new task frame ----------
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую задачу", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_task_entry = ttk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Тип:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_task_type = ttk.Combobox(add_frame, values=["учеба", "спорт", "работа"], state="readonly")
        self.new_task_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.new_task_type.current(0)

        add_btn = ttk.Button(add_frame, text="Добавить задачу", command=self.add_new_task)
        add_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # ---------- Current tasks pool summary ----------
        pool_frame = ttk.LabelFrame(self.root, text="Доступные задачи (всего)", padding=5)
        pool_frame.pack(fill="x", padx=10, pady=5)

        self.pool_label = ttk.Label(pool_frame, text="", font=("Arial", 9))
        self.pool_label.pack()
        self._refresh_pool_display()

    def generate_task(self):
        task = self.manager.generate_random_task()
        if not task:
            messagebox.showwarning("Нет задач", "Сначала добавьте хотя бы одну задачу!")
            return
        self.manager.add_to_history(task)
        self.current_task_label.config(text=f"✓ {task['name']} ({task['type']})")
        self._refresh_history_display()
        self._refresh_pool_display()

    def add_new_task(self):
        name = self.new_task_entry.get()
        task_type = self.new_task_type.get()
        if not name.strip():
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        if self.manager.add_task(name, task_type):
            messagebox.showinfo("Успех", f"Задача «{name}» добавлена.")
            self.new_task_entry.delete(0, tk.END)
            self._refresh_pool_display()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить задачу.")

    def _refresh_history_display(self):
        """Update the listbox according to current filter."""
        self.history_listbox.delete(0, tk.END)
        filtered = self.manager.get_filtered_history(self.current_filter.get())
        if not filtered:
            self.history_listbox.insert(tk.END, " (Нет записей) ")
        else:
            for entry in reversed(filtered):   # show newest first
                line = f"{entry['timestamp']}  |  {entry['name']}  [{entry['type']}]"
                self.history_listbox.insert(tk.END, line)

    def _refresh_pool_display(self):
        """Show total number of available tasks and a brief preview."""
        total = len(self.manager.tasks)
        preview = ", ".join([f"{t['name'][:15]}..." for t in self.manager.tasks[:3]])
        if total > 3:
            preview += f" и ещё {total-3}"
        self.pool_label.config(text=f"Всего задач: {total}   |   Примеры: {preview}")

# ---------------------------- Main ----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGeneratorApp(root)
    root.mainloop()