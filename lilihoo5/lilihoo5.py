import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class QuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Предопределённые цитаты
        self.default_quotes = [
            {"text": "Будь изменением, которое хочешь видеть в мире.", "author": "Махатма Ганди", "theme": "Мотивация"},
            {"text": "Жизнь - это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "theme": "Жизнь"},
            {"text": "Воображение важнее знания.", "author": "Альберт Эйнштейн", "theme": "Знание"},
            {"text": "Единственный способ делать великую работу - любить то, что ты делаешь.", "author": "Стив Джобс", "theme": "Работа"},
            {"text": "Не судите о моих успехах по моим неудачам.", "author": "Дж.К. Роулинг", "theme": "Успех"},
            {"text": "Сложнее всего начать действовать, остальное зависит от упорства.", "author": "Пауло Коэльо", "theme": "Мотивация"},
            {"text": "В 60 лет вы поймёте, что жизнь начинается в 40.", "author": "Фаина Раневская", "theme": "Жизнь"},
            {"text": "Знание - сила.", "author": "Фрэнсис Бэкон", "theme": "Знание"},
            {"text": "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "theme": "Успех"},
            {"text": "Делай, что можешь, с тем, что имеешь, там, где ты есть.", "author": "Теодор Рузвельт", "theme": "Мотивация"}
        ]
        
        # Загрузка истории
        self.history = []
        self.all_quotes = []
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление списков фильтров
        self.update_filter_lists()
        
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === Верхняя панель с текущей цитатой ===
        quote_frame = ttk.LabelFrame(main_frame, text="Текущая цитата", padding="10")
        quote_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        quote_frame.columnconfigure(0, weight=1)
        
        self.current_quote_text = tk.StringVar()
        self.current_quote_text.set("Нажмите кнопку, чтобы получить цитату")
        
        quote_display = tk.Text(quote_frame, height=4, wrap=tk.WORD, font=("Arial", 12))
        quote_display.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        quote_display.insert("1.0", self.current_quote_text.get())
        quote_display.config(state="disabled")
        self.quote_display = quote_display
        
        # Кнопка генерации
        generate_btn = ttk.Button(quote_frame, text="Сгенерировать цитату", command=self.generate_quote)
        generate_btn.grid(row=1, column=0)
        
        # === Панель фильтрации ===
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Фильтр по автору
        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=(0, 5))
        self.author_filter = ttk.Combobox(filter_frame, values=["Все"], state="readonly", width=25)
        self.author_filter.grid(row=0, column=1, padx=(0, 10))
        self.author_filter.set("Все")
        self.author_filter.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Фильтр по теме
        ttk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=(0, 5))
        self.theme_filter = ttk.Combobox(filter_frame, values=["Все"], state="readonly", width=20)
        self.theme_filter.grid(row=0, column=3, padx=(0, 10))
        self.theme_filter.set("Все")
        self.theme_filter.bind("<<ComboboxSelected>>", self.apply_filters)
        
        # Кнопка сброса фильтров
        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.grid(row=0, column=4)
        
        # === История цитат ===
        history_frame = ttk.LabelFrame(main_frame, text="История цитат", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Список истории с прокруткой
        scrollbar = ttk.Scrollbar(history_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.history_listbox.yview)
        
        # === Панель добавления новой цитаты ===
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую цитату", padding="10")
        add_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        add_frame.columnconfigure(1, weight=1)
        
        # Текст цитаты
        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.new_quote_text = tk.Text(add_frame, height=3, wrap=tk.WORD)
        self.new_quote_text.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Автор
        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.new_author = ttk.Entry(add_frame, width=30)
        self.new_author.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Тема
        ttk.Label(add_frame, text="Тема:").grid(row=1, column=2, sticky=tk.W, pady=(0, 5), padx=(10, 0))
        self.new_theme = ttk.Entry(add_frame, width=20)
        self.new_theme.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=(0, 5), padx=(5, 0))
        
        # Кнопка добавления
        add_btn = ttk.Button(add_frame, text="Добавить цитату", command=self.add_quote)
        add_btn.grid(row=2, column=1, columnspan=2, pady=(10, 0))
        
        # Статистика
        self.stats_label = ttk.Label(main_frame, text="", font=("Arial", 9))
        self.stats_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        self.update_stats()
        
    def load_data(self):
        """Загрузка истории и цитат из JSON"""
        # Загрузка истории
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []
        
        # Загрузка пользовательских цитат
        if os.path.exists("custom_quotes.json"):
            try:
                with open("custom_quotes.json", "r", encoding="utf-8") as f:
                    custom_quotes = json.load(f)
                self.all_quotes = self.default_quotes + custom_quotes
            except:
                self.all_quotes = self.default_quotes.copy()
        else:
            self.all_quotes = self.default_quotes.copy()
    
    def save_data(self):
        """Сохранение истории в JSON"""
        try:
            with open("history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def save_custom_quotes(self):
        """Сохранение пользовательских цитат"""
        custom_quotes = [q for q in self.all_quotes if q not in self.default_quotes]
        try:
            with open("custom_quotes.json", "w", encoding="utf-8") as f:
                json.dump(custom_quotes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить цитаты: {e}")
    
    def generate_quote(self):
        """Генерация случайной цитаты"""
        if not self.all_quotes:
            messagebox.showwarning("Внимание", "Нет доступных цитат. Добавьте новые!")
            return
        
        quote = random.choice(self.all_quotes)
        
        # Добавление в историю с временной меткой
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = {
            "text": quote["text"],
            "author": quote["author"],
            "theme": quote["theme"],
            "timestamp": timestamp
        }
        self.history.insert(0, history_entry)
        self.save_data()
        
        # Отображение цитаты
        self.quote_display.config(state="normal")
        self.quote_display.delete("1.0", tk.END)
        display_text = f'"{quote["text"]}"\n\n— {quote["author"]} ({quote["theme"]})'
        self.quote_display.insert("1.0", display_text)
        self.quote_display.config(state="disabled")
        
        # Обновление истории и статистики
        self.apply_filters()
        self.update_stats()
    
    def update_filter_lists(self):
        """Обновление списков для фильтрации"""
        authors = sorted(set(["Все"] + [q["author"] for q in self.history]))
        themes = sorted(set(["Все"] + [q["theme"] for q in self.history]))
        
        # Сохраняем текущие значения
        current_author = self.author_filter.get() if hasattr(self, 'author_filter') else "Все"
        current_theme = self.theme_filter.get() if hasattr(self, 'theme_filter') else "Все"
        
        if hasattr(self, 'author_filter'):
            self.author_filter['values'] = authors
            self.author_filter.set(current_author if current_author in authors else "Все")
            
            self.theme_filter['values'] = themes
            self.theme_filter.set(current_theme if current_theme in themes else "Все")
    
    def apply_filters(self, event=None):
        """Применение фильтров к истории"""
        self.history_listbox.delete(0, tk.END)
        
        author = self.author_filter.get()
        theme = self.theme_filter.get()
        
        filtered_history = self.history
        
        if author != "Все":
            filtered_history = [q for q in filtered_history if q["author"] == author]
        
        if theme != "Все":
            filtered_history = [q for q in filtered_history if q["theme"] == theme]
        
        for entry in filtered_history:
            display_text = f'[{entry["timestamp"]}] "{entry["text"][:50]}{"..." if len(entry["text"]) > 50 else ""}" — {entry["author"]} ({entry["theme"]})'
            self.history_listbox.insert(tk.END, display_text)
        
        # Обновление статистики фильтрации
        self.update_filter_stats(len(filtered_history), len(self.history))
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.author_filter.set("Все")
        self.theme_filter.set("Все")
        self.apply_filters()
    
    def update_stats(self):
        """Обновление общей статистики"""
        total_quotes = len(self.all_quotes)
        total_history = len(self.history)
        authors_count = len(set([q["author"] for q in self.all_quotes]))
        themes_count = len(set([q["theme"] for q in self.all_quotes]))
        
        stats_text = f"📊 Всего цитат: {total_quotes} | Авторов: {authors_count} | Тем: {themes_count} | История: {total_history}"
        self.stats_label.config(text=stats_text)
    
    def update_filter_stats(self, filtered_count, total_count):
        """Обновление статистики фильтрации"""
        current_stats = self.stats_label.cget("text")
        if " | Показано:" not in current_stats:
            current_stats += f" | Показано: {filtered_count}/{total_count}"
        else:
            parts = current_stats.split(" | Показано:")
            current_stats = f"{parts[0]} | Показано: {filtered_count}/{total_count}"
        self.stats_label.config(text=current_stats)
    
    def add_quote(self):
        """Добавление новой цитаты с проверкой ввода"""
        # Проверка на пустые строки
        text = self.new_quote_text.get("1.0", tk.END).strip()
        author = self.new_author.get().strip()
        theme = self.new_theme.get().strip()
        
        if not text:
            messagebox.showerror("Ошибка", "Текст цитаты не может быть пустым!")
            return
        
        if not author:
            messagebox.showerror("Ошибка", "Автор не может быть пустым!")
            return
        
        if not theme:
            messagebox.showerror("Ошибка", "Тема не может быть пустой!")
            return
        
        # Добавление цитаты
        new_quote = {
            "text": text,
            "author": author,
            "theme": theme
        }
        
        self.all_quotes.append(new_quote)
        self.save_custom_quotes()
        
        # Очистка полей
        self.new_quote_text.delete("1.0", tk.END)
        self.new_author.delete(0, tk.END)
        self.new_theme.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")
        
        # Обновление статистики
        self.update_stats()
    
    def on_closing(self):
        """Действия при закрытии приложения"""
        self.save_data()
        self.save_custom_quotes()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = QuoteGenerator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()