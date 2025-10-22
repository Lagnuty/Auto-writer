import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import keyboard
import pyautogui
import sys
import random
import json
import os
from datetime import datetime
import pickle
from cryptography.fernet import Fernet

class TextTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматический набор текста Pro")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Переменные настроек
        self.settings = {
            'hotkey': 'F6',
            'stop_hotkey': 'F7',
            'typing_speed': 50,
            'use_random_speed': False,
            'speed_variation': 5,
            'use_tray': True,
            'auto_save': True,
            'global_hotkeys': True,
            'dark_theme': False,
            'minimal_mode': False,
            'multilanguage': False,
            'simulate_errors': False,
            'error_rate': 5,
            'paragraph_pause': True,
            'pause_duration': 1.0,
            'encrypt_data': False,
            'auto_clear': False,
            'clear_delay': 10,
            'show_progress': True,
            'show_stats': True
        }
        
        # Данные приложения
        self.is_listening = False
        self.is_typing = False
        self.hotkey_listener = None
        self.stop_hotkey_listener = None
        self.text_history = []
        self.profiles = {}
        self.current_profile = "default"
        self.stats = {'total_chars': 0, 'total_time': 0, 'sessions': 0}
        self.templates = {
            "Приветствие": "Здравствуйте!",
            "Благодарность": "Спасибо за ваше сообщение!",
            "Вопрос": "Не могли бы вы уточнить этот момент?",
            "Подпись": "С уважением,\n[Ваше имя]"
        }
        
        # Ключ шифрования
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        self.setup_data_folder()
        self.load_settings()
        self.load_data()
        self.create_widgets()
        self.setup_hotkeys()
        self.apply_theme()
        self.setup_auto_save()
        
    def setup_data_folder(self):
        """Создает папку для данных приложения"""
        self.data_folder = os.path.join(os.path.expanduser("~"), ".text_typer_pro")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            
    def load_settings(self):
        """Загружает настройки из файла"""
        settings_file = os.path.join(self.data_folder, "settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except:
                pass
                
    def save_settings(self):
        """Сохраняет настройки в файл"""
        settings_file = os.path.join(self.data_folder, "settings.json")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass
            
    def load_data(self):
        """Загружает дополнительные данные"""
        # Загрузка истории
        history_file = os.path.join(self.data_folder, "history.dat")
        if os.path.exists(history_file):
            try:
                if self.settings['encrypt_data']:
                    with open(history_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    self.text_history = pickle.loads(decrypted_data)
                else:
                    with open(history_file, 'rb') as f:
                        self.text_history = pickle.load(f)
            except:
                self.text_history = []
                
        # Загрузка профилей
        profiles_file = os.path.join(self.data_folder, "profiles.dat")
        if os.path.exists(profiles_file):
            try:
                if self.settings['encrypt_data']:
                    with open(profiles_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    self.profiles = pickle.loads(decrypted_data)
                else:
                    with open(profiles_file, 'rb') as f:
                        self.profiles = pickle.load(f)
            except:
                self.profiles = {}
                
        # Загрузка статистики
        stats_file = os.path.join(self.data_folder, "stats.dat")
        if os.path.exists(stats_file):
            try:
                if self.settings['encrypt_data']:
                    with open(stats_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    self.stats = pickle.loads(decrypted_data)
                else:
                    with open(stats_file, 'rb') as f:
                        self.stats = pickle.load(f)
            except:
                self.stats = {'total_chars': 0, 'total_time': 0, 'sessions': 0}
                
        # Загрузка шаблонов
        templates_file = os.path.join(self.data_folder, "templates.dat")
        if os.path.exists(templates_file):
            try:
                if self.settings['encrypt_data']:
                    with open(templates_file, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    loaded_templates = pickle.loads(decrypted_data)
                    self.templates.update(loaded_templates)
                else:
                    with open(templates_file, 'rb') as f:
                        loaded_templates = pickle.load(f)
                        self.templates.update(loaded_templates)
            except:
                pass
                
    def save_data(self):
        """Сохраняет дополнительные данные"""
        # Сохранение истории
        history_file = os.path.join(self.data_folder, "history.dat")
        try:
            if self.settings['encrypt_data']:
                encrypted_data = self.cipher_suite.encrypt(pickle.dumps(self.text_history))
                with open(history_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(history_file, 'wb') as f:
                    pickle.dump(self.text_history, f)
        except:
            pass
            
        # Сохранение профилей
        profiles_file = os.path.join(self.data_folder, "profiles.dat")
        try:
            if self.settings['encrypt_data']:
                encrypted_data = self.cipher_suite.encrypt(pickle.dumps(self.profiles))
                with open(profiles_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(profiles_file, 'wb') as f:
                    pickle.dump(self.profiles, f)
        except:
            pass
            
        # Сохранение статистики
        stats_file = os.path.join(self.data_folder, "stats.dat")
        try:
            if self.settings['encrypt_data']:
                encrypted_data = self.cipher_suite.encrypt(pickle.dumps(self.stats))
                with open(stats_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(stats_file, 'wb') as f:
                    pickle.dump(self.stats, f)
        except:
            pass
            
        # Сохранение шаблонов
        templates_file = os.path.join(self.data_folder, "templates.dat")
        try:
            if self.settings['encrypt_data']:
                encrypted_data = self.cipher_suite.encrypt(pickle.dumps(self.templates))
                with open(templates_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                with open(templates_file, 'wb') as f:
                    pickle.dump(self.templates, f)
        except:
            pass

    def create_widgets(self):
        # Верхняя панель с кнопкой справки и быстрыми действиями
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_btn = ttk.Button(top_frame, text="?", width=2, command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        ttk.Label(top_frame, text="Автоматический набор текста Pro", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        
        # Кнопки быстрого доступа
        quick_actions = ttk.Frame(top_frame)
        quick_actions.pack(side=tk.RIGHT)
        
        ttk.Button(quick_actions, text="Настройки", command=self.show_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_actions, text="Минимальный режим", command=self.toggle_minimal_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_actions, text="История", command=self.show_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_actions, text="Профили", command=self.show_profiles).pack(side=tk.LEFT, padx=2)
        
        # Основной контейнер
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.create_main_interface()
        
    def create_main_interface(self):
        # Очищаем основной контейнер
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        if self.settings['minimal_mode']:
            self.create_minimal_interface()
        else:
            self.create_full_interface()
            
    def create_full_interface(self):
        # Левая панель - текст и основные настройки
        left_frame = ttk.Frame(self.main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Поле для ввода текста с вкладками
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Вкладка основного текста
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="Основной текст")
        
        self.text_area = scrolledtext.ScrolledText(text_frame, height=12, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка шаблонов
        templates_frame = ttk.Frame(notebook)
        notebook.add(templates_frame, text="Шаблоны")
        self.setup_templates_tab(templates_frame)
        
        # Панель управления текстом
        text_controls = ttk.Frame(left_frame)
        text_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(text_controls, text="Импорт из файла", command=self.import_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(text_controls, text="Из буфера обмена", command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(text_controls, text="Экспорт в файл", command=self.export_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(text_controls, text="Очистить", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # Правая панель - настройки и управление
        right_frame = ttk.Frame(self.main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Быстрые настройки
        quick_settings = ttk.LabelFrame(right_frame, text="Быстрые настройки", padding=10)
        quick_settings.pack(fill=tk.X, pady=(0, 10))
        
        # Скорость набора
        ttk.Label(quick_settings, text="Скорость:").grid(row=0, column=0, sticky=tk.W)
        self.speed_var = tk.StringVar(value=str(self.settings['typing_speed']))
        speed_scale = ttk.Scale(quick_settings, from_=10, to=200, orient=tk.HORIZONTAL,
                               variable=self.speed_var, command=self.on_speed_change)
        speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.speed_label = ttk.Label(quick_settings, text=f"{self.settings['typing_speed']} сим/мин")
        self.speed_label.grid(row=0, column=2, sticky=tk.W)
        
        # Случайная скорость
        self.random_var = tk.BooleanVar(value=self.settings['use_random_speed'])
        ttk.Checkbutton(quick_settings, text="Случайная скорость", variable=self.random_var,
                       command=self.on_random_speed_change).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Имитация ошибок
        self.errors_var = tk.BooleanVar(value=self.settings['simulate_errors'])
        ttk.Checkbutton(quick_settings, text="Имитация ошибок", variable=self.errors_var,
                       command=self.on_errors_change).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Горячие клавиши
        ttk.Label(quick_settings, text="Старт:").grid(row=3, column=0, sticky=tk.W)
        self.hotkey_var = tk.StringVar(value=self.settings['hotkey'])
        hotkey_combo = ttk.Combobox(quick_settings, textvariable=self.hotkey_var, 
                                   values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                   state="readonly", width=8)
        hotkey_combo.grid(row=3, column=1, sticky=tk.W, padx=5)
        hotkey_combo.bind('<<ComboboxSelected>>', self.on_hotkey_change)
        
        ttk.Label(quick_settings, text="Стоп:").grid(row=4, column=0, sticky=tk.W)
        self.stop_hotkey_var = tk.StringVar(value=self.settings['stop_hotkey'])
        stop_hotkey_combo = ttk.Combobox(quick_settings, textvariable=self.stop_hotkey_var, 
                                        values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                        state="readonly", width=8)
        stop_hotkey_combo.grid(row=4, column=1, sticky=tk.W, padx=5)
        stop_hotkey_combo.bind('<<ComboboxSelected>>', self.on_stop_hotkey_change)
        
        quick_settings.columnconfigure(1, weight=1)
        
        # Управление
        control_frame = ttk.LabelFrame(right_frame, text="Управление", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="Запустить прослушивание", command=self.toggle_listening)
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.stop_button = ttk.Button(control_frame, text="Остановить набор", command=self.stop_typing, state="disabled")
        self.stop_button.pack(fill=tk.X, pady=2)
        
        ttk.Button(control_frame, text="Тестировать набор", command=self.test_typing).pack(fill=tk.X, pady=2)
        
        # Прогресс и статистика
        if self.settings['show_progress']:
            progress_frame = ttk.LabelFrame(right_frame, text="Прогресс", padding=10)
            progress_frame.pack(fill=tk.X, pady=(0, 10))
            
            self.progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
            progress_bar.pack(fill=tk.X)
            
            self.progress_label = ttk.Label(progress_frame, text="Готов")
            self.progress_label.pack()
            
        if self.settings['show_stats']:
            stats_frame = ttk.LabelFrame(right_frame, text="Статистика", padding=10)
            stats_frame.pack(fill=tk.X)
            
            self.stats_label = ttk.Label(stats_frame, text=self.get_stats_text())
            self.stats_label.pack()
        
        # Индикатор состояния
        self.state_indicator = ttk.Label(right_frame, text="⏹️ Не печатает", foreground="red")
        self.state_indicator.pack(pady=10)
        
    def create_minimal_interface(self):
        # Минималистичный интерфейс
        minimal_frame = ttk.Frame(self.main_container)
        minimal_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = scrolledtext.ScrolledText(minimal_frame, height=8, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        controls_frame = ttk.Frame(minimal_frame)
        controls_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(controls_frame, text="▶", width=3, command=self.toggle_listening)
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(controls_frame, text="⏹", width=3, command=self.stop_typing, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls_frame, text="⚙", width=3, command=self.show_settings).pack(side=tk.RIGHT)
        
        self.state_indicator = ttk.Label(controls_frame, text="Готов")
        self.state_indicator.pack(side=tk.LEFT, padx=10)
        
    def setup_templates_tab(self, parent):
        """Настраивает вкладку шаблонов"""
        # Список шаблонов
        templates_list_frame = ttk.Frame(parent)
        templates_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        ttk.Label(templates_list_frame, text="Шаблоны:").pack(anchor=tk.W)
        
        self.templates_listbox = tk.Listbox(templates_list_frame, width=20, height=10)
        self.templates_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Обновляем список шаблонов
        self.update_templates_list()
        
        # Кнопки управления шаблонами
        templates_buttons = ttk.Frame(templates_list_frame)
        templates_buttons.pack(fill=tk.X)
        
        ttk.Button(templates_buttons, text="Добавить", command=self.add_template).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(templates_buttons, text="Удалить", command=self.delete_template).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Просмотр и редактирование шаблона
        template_edit_frame = ttk.Frame(parent)
        template_edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(template_edit_frame, text="Текст шаблона:").pack(anchor=tk.W)
        
        self.template_text = scrolledtext.ScrolledText(template_edit_frame, height=8, wrap=tk.WORD)
        self.template_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(template_edit_frame, text="Вставить шаблон", 
                  command=self.insert_template).pack(fill=tk.X, pady=2)
        ttk.Button(template_edit_frame, text="Сохранить изменения", 
                  command=self.save_template).pack(fill=tk.X, pady=2)
        
        # Привязываем событие выбора шаблона
        self.templates_listbox.bind('<<ListboxSelect>>', self.on_template_select)

    def update_templates_list(self):
        """Обновляет список шаблонов"""
        self.templates_listbox.delete(0, tk.END)
        for name in self.templates.keys():
            self.templates_listbox.insert(tk.END, name)

    def on_template_select(self, event):
        """Обрабатывает выбор шаблона"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            template_text = self.templates.get(template_name, "")
            self.template_text.delete(1.0, tk.END)
            self.template_text.insert(1.0, template_text)

    def add_template(self):
        """Добавляет новый шаблон"""
        name = tk.simpledialog.askstring("Новый шаблон", "Введите название шаблона:")
        if name:
            self.templates[name] = ""
            self.update_templates_list()
            self.save_data()

    def delete_template(self):
        """Удаляет выбранный шаблон"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            if messagebox.askyesno("Подтверждение", f"Удалить шаблон '{template_name}'?"):
                del self.templates[template_name]
                self.update_templates_list()
                self.template_text.delete(1.0, tk.END)
                self.save_data()

    def save_template(self):
        """Сохраняет изменения в шаблоне"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            new_text = self.template_text.get(1.0, tk.END).strip()
            self.templates[template_name] = new_text
            self.save_data()
            messagebox.showinfo("Успех", "Шаблон сохранен")

    def insert_template(self):
        """Вставляет выбранный шаблон в основное текстовое поле"""
        selection = self.templates_listbox.curselection()
        if selection:
            template_name = self.templates_listbox.get(selection[0])
            template_text = self.templates.get(template_name, "")
            self.text_area.insert(tk.INSERT, template_text)

    def on_speed_change(self, value):
        speed = int(float(value))
        self.settings['typing_speed'] = speed
        self.speed_label.config(text=f"{speed} сим/мин")
        
    def on_random_speed_change(self):
        self.settings['use_random_speed'] = self.random_var.get()
        
    def on_errors_change(self):
        self.settings['simulate_errors'] = self.errors_var.get()
        
    def on_hotkey_change(self, event=None):
        new_hotkey = self.hotkey_var.get()
        if new_hotkey != self.settings['hotkey']:
            self.settings['hotkey'] = new_hotkey
            self.setup_hotkeys()
            
    def on_stop_hotkey_change(self, event=None):
        new_hotkey = self.stop_hotkey_var.get()
        if new_hotkey != self.settings['stop_hotkey']:
            self.settings['stop_hotkey'] = new_hotkey
            self.setup_hotkeys()
            
    def setup_hotkeys(self):
        """Настраивает глобальные горячие клавиши"""
        # Удаляем старые хоткеи если были
        if self.hotkey_listener:
            try:
                keyboard.remove_hotkey(self.hotkey_listener)
            except:
                pass
        if self.stop_hotkey_listener:
            try:
                keyboard.remove_hotkey(self.stop_hotkey_listener)
            except:
                pass
        
        try:
            self.hotkey_listener = keyboard.add_hotkey(
                self.settings['hotkey'], 
                self.on_hotkey_pressed
            )
            self.stop_hotkey_listener = keyboard.add_hotkey(
                self.settings['stop_hotkey'], 
                self.on_stop_hotkey_pressed
            )
        except Exception as e:
            print(f"Ошибка настройки горячих клавиш: {e}")
            
    def on_hotkey_pressed(self):
        if self.is_listening and not self.is_typing:
            text_to_type = self.text_area.get(1.0, tk.END).strip()
            if text_to_type:
                thread = threading.Thread(target=self.type_text, args=(text_to_type,))
                thread.daemon = True
                thread.start()
            else:
                self.show_status("Ошибка: нет текста для ввода")
                
    def on_stop_hotkey_pressed(self):
        self.stop_typing()
            
    def stop_typing(self):
        if self.is_typing:
            self.is_typing = False
            self.show_status("Набор текста остановлен")
            self.update_state_indicator()
            
    def type_text(self, text):
        """Улучшенная функция набора текста с поддержкой новых функций"""
        try:
            self.is_typing = True
            self.update_state_indicator()
            start_time = time.time()
            
            # Сохраняем в историю
            if text.strip() and text not in self.text_history:
                self.text_history.append(text)
                if len(self.text_history) > 50:
                    self.text_history.pop(0)
            
            # Небольшая задержка перед началом набора
            time.sleep(0.5)
            
            total_chars = len(text)
            typed_chars = 0
            
            i = 0
            while i < len(text) and self.is_typing:
                char = text[i]
                
                # Обработка ошибок (если включено)
                if (self.settings['simulate_errors'] and 
                    random.randint(1, 100) <= self.settings['error_rate'] and
                    char not in [' ', '\n', '\t']):
                    
                    # Генерируем случайную ошибку
                    wrong_char = self.get_wrong_char(char)
                    pyautogui.write(wrong_char)
                    time.sleep(0.1)
                    
                    # Стираем ошибку и пишем правильно
                    pyautogui.press('backspace')
                    time.sleep(0.1)
                    pyautogui.write(char)
                    
                else:
                    pyautogui.write(char)
                
                # Пауза между абзацами
                if (self.settings['paragraph_pause'] and char == '\n' and 
                    i + 1 < len(text) and text[i + 1] == '\n'):
                    time.sleep(self.settings['pause_duration'])
                
                # Рассчитываем задержку
                if self.settings['use_random_speed']:
                    current_speed = self.settings['typing_speed'] + random.randint(
                        -self.settings['speed_variation'], self.settings['speed_variation'])
                    current_speed = max(10, current_speed)
                else:
                    current_speed = self.settings['typing_speed']
                    
                delay_per_char = 60.0 / current_speed
                variation = random.uniform(0.8, 1.2)
                time.sleep(delay_per_char * variation)
                
                # Обновляем прогресс
                typed_chars += 1
                if self.settings['show_progress'] and hasattr(self, 'progress_var'):
                    progress = (typed_chars / total_chars) * 100
                    self.progress_var.set(progress)
                    if hasattr(self, 'progress_label'):
                        self.progress_label.config(text=f"{typed_chars}/{total_chars} символов")
                
                i += 1
                
            # Обновляем статистику
            if self.is_typing:
                end_time = time.time()
                typing_time = end_time - start_time
                self.stats['total_chars'] += typed_chars
                self.stats['total_time'] += typing_time
                self.stats['sessions'] += 1
                
                self.show_status("Текст успешно введен")
                self.update_stats_display()
                
                # Автоочистка если включено
                if self.settings['auto_clear']:
                    self.root.after(self.settings['clear_delay'] * 1000, self.clear_text)
                    
            else:
                self.show_status("Набор текста прерван")
                
            self.is_typing = False
            self.update_state_indicator()
            if hasattr(self, 'progress_var'):
                self.progress_var.set(0)
            if hasattr(self, 'progress_label'):
                self.progress_label.config(text="Готов")
            
            # Автосохранение
            if self.settings['auto_save']:
                self.save_data()
            
        except Exception as e:
            self.show_status(f"Ошибка при вводе текста: {str(e)}")
            self.is_typing = False
            self.update_state_indicator()

    def get_wrong_char(self, correct_char):
        """Генерирует неправильный символ для имитации ошибки"""
        keyboard_layout = {
            'а': 'ф', 'б': 'и', 'в': 'ы', 'г': 'о', 'д': 'л', 'е': 'э', 'ё': 'э',
            'ж': 'э', 'з': 'я', 'и': 'б', 'й': 'ц', 'к': 'у', 'л': 'д', 'м': 'ь',
            'н': 'т', 'о': 'г', 'п': 'ш', 'р': 'к', 'с': 'ы', 'т': 'н', 'у': 'к',
            'ф': 'а', 'х': 'з', 'ц': 'й', 'ч': 'с', 'ш': 'п', 'щ': 'р', 'ъ': 'ю',
            'ы': 'в', 'ь': 'м', 'э': 'е', 'ю': 'ъ', 'я': 'з',
            'a': 's', 's': 'a', 'd': 'f', 'f': 'd', 'g': 'h', 'h': 'g',
            'j': 'k', 'k': 'j', 'l': ';', ';': 'l',
            'q': 'w', 'w': 'q', 'e': 'r', 'r': 'e', 't': 'y', 'y': 't',
            'u': 'i', 'i': 'u', 'o': 'p', 'p': 'o',
            'z': 'x', 'x': 'z', 'c': 'v', 'v': 'c', 'b': 'n', 'n': 'b',
            'm': ',', ',': 'm'
        }
        return keyboard_layout.get(correct_char.lower(), correct_char)

    def show_status(self, message):
        """Показывает статус в основном интерфейсе"""
        if hasattr(self, 'state_indicator'):
            self.state_indicator.config(text=message)
        print(message)

    def update_state_indicator(self):
        if self.is_typing:
            if hasattr(self, 'state_indicator'):
                self.state_indicator.config(text="🟢 Печатает...", foreground="green")
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state="normal")
        else:
            if hasattr(self, 'state_indicator'):
                self.state_indicator.config(text="⏹️ Не печатает", foreground="red")
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state="disabled")
            
    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.start_button.config(text="Остановить прослушивание")
            self.show_status(f"Прослушивание активно. Нажмите {self.settings['hotkey']} для ввода")
        else:
            self.start_button.config(text="Запустить прослушивание")
            self.show_status("Прослушивание остановлено")
            
    def test_typing(self):
        text_to_type = self.text_area.get(1.0, tk.END).strip()
        if text_to_type:
            self.show_status("Тестирование набора...")
            thread = threading.Thread(target=self.type_text, args=(text_to_type,))
            thread.daemon = True
            thread.start()
        else:
            messagebox.showwarning("Предупреждение", "Введите текст для тестирования")
            
    def clear_text(self):
        self.text_area.delete(1.0, tk.END)
        self.show_status("Текст очищен")

    def show_settings(self):
        """Показывает окно настроек"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки")
        settings_window.geometry("600x500")
        settings_window.resizable(False, False)
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка основных настроек
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Основные")
        self.setup_basic_settings(basic_frame)
        
        # Вкладка дополнительных настроек
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Дополнительно")
        self.setup_advanced_settings(advanced_frame)
        
        # Вкладка безопасности
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text="Безопасность")
        self.setup_security_settings(security_frame)
        
        # Кнопки сохранения/отмены
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Сохранить", command=lambda: self.save_all_settings(settings_window)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Отмена", command=settings_window.destroy).pack(side=tk.RIGHT)

    def setup_basic_settings(self, parent):
        """Настраивает вкладку основных настроек"""
        # Скорость набора
        speed_frame = ttk.Frame(parent)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Базовая скорость:").grid(row=0, column=0, sticky=tk.W)
        speed_var = tk.StringVar(value=str(self.settings['typing_speed']))
        speed_scale = ttk.Scale(speed_frame, from_=10, to=200, orient=tk.HORIZONTAL,
                               variable=speed_var, command=lambda v: speed_var.set(str(int(float(v)))))
        speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=5)
        speed_label = ttk.Label(speed_frame, text=f"{self.settings['typing_speed']} сим/мин")
        speed_label.grid(row=0, column=2, sticky=tk.W)
        
        def update_speed_label(*args):
            speed_label.config(text=f"{speed_var.get()} сим/мин")
        speed_var.trace('w', update_speed_label)
        
        # Случайная скорость
        random_frame = ttk.Frame(parent)
        random_frame.pack(fill=tk.X, pady=5)
        
        random_var = tk.BooleanVar(value=self.settings['use_random_speed'])
        ttk.Checkbutton(random_frame, text="Случайная скорость", variable=random_var).pack(side=tk.LEFT)
        
        ttk.Label(random_frame, text="Разброс:").pack(side=tk.LEFT, padx=(20, 5))
        variation_var = tk.StringVar(value=str(self.settings['speed_variation']))
        variation_spin = ttk.Spinbox(random_frame, from_=1, to=20, width=5, textvariable=variation_var)
        variation_spin.pack(side=tk.LEFT)
        ttk.Label(random_frame, text="сим/мин").pack(side=tk.LEFT, padx=5)
        
        # Горячие клавиши
        hotkeys_frame = ttk.LabelFrame(parent, text="Горячие клавиши", padding=10)
        hotkeys_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(hotkeys_frame, text="Старт:").grid(row=0, column=0, sticky=tk.W)
        hotkey_var = tk.StringVar(value=self.settings['hotkey'])
        hotkey_combo = ttk.Combobox(hotkeys_frame, textvariable=hotkey_var, 
                                   values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                   state="readonly", width=8)
        hotkey_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(hotkeys_frame, text="Стоп:").grid(row=1, column=0, sticky=tk.W)
        stop_hotkey_var = tk.StringVar(value=self.settings['stop_hotkey'])
        stop_hotkey_combo = ttk.Combobox(hotkeys_frame, textvariable=stop_hotkey_var, 
                                        values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                        state="readonly", width=8)
        stop_hotkey_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        global_var = tk.BooleanVar(value=self.settings['global_hotkeys'])
        ttk.Checkbutton(hotkeys_frame, text="Глобальные горячие клавиши", variable=global_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5,0))
        
        # Сохраняем ссылки на переменные для использования в save_all_settings
        self.temp_settings_vars = {
            'typing_speed': speed_var,
            'use_random_speed': random_var,
            'speed_variation': variation_var,
            'hotkey': hotkey_var,
            'stop_hotkey': stop_hotkey_var,
            'global_hotkeys': global_var
        }

    def setup_advanced_settings(self, parent):
        """Настраивает вкладку дополнительных настроек"""
        # Имитация ошибок
        errors_frame = ttk.Frame(parent)
        errors_frame.pack(fill=tk.X, pady=5)
        
        errors_var = tk.BooleanVar(value=self.settings['simulate_errors'])
        ttk.Checkbutton(errors_frame, text="Имитация ошибок", variable=errors_var).pack(side=tk.LEFT)
        
        ttk.Label(errors_frame, text="Частота ошибок:").pack(side=tk.LEFT, padx=(20, 5))
        error_rate_var = tk.StringVar(value=str(self.settings['error_rate']))
        error_rate_spin = ttk.Spinbox(errors_frame, from_=1, to=50, width=5, textvariable=error_rate_var)
        error_rate_spin.pack(side=tk.LEFT)
        ttk.Label(errors_frame, text="%").pack(side=tk.LEFT, padx=5)
        
        # Пауза между абзацами
        paragraph_frame = ttk.Frame(parent)
        paragraph_frame.pack(fill=tk.X, pady=5)
        
        paragraph_var = tk.BooleanVar(value=self.settings['paragraph_pause'])
        ttk.Checkbutton(paragraph_frame, text="Пауза между абзацами", variable=paragraph_var).pack(side=tk.LEFT)
        
        ttk.Label(paragraph_frame, text="Длительность:").pack(side=tk.LEFT, padx=(20, 5))
        pause_var = tk.StringVar(value=str(self.settings['pause_duration']))
        pause_spin = ttk.Spinbox(paragraph_frame, from_=0.5, to=5.0, increment=0.5, width=5, textvariable=pause_var)
        pause_spin.pack(side=tk.LEFT)
        ttk.Label(paragraph_frame, text="сек").pack(side=tk.LEFT, padx=5)
        
        # Интерфейс
        interface_frame = ttk.LabelFrame(parent, text="Интерфейс", padding=10)
        interface_frame.pack(fill=tk.X, pady=5)
        
        dark_var = tk.BooleanVar(value=self.settings['dark_theme'])
        ttk.Checkbutton(interface_frame, text="Темная тема", variable=dark_var).pack(anchor=tk.W)
        
        progress_var = tk.BooleanVar(value=self.settings['show_progress'])
        ttk.Checkbutton(interface_frame, text="Показывать прогресс", variable=progress_var).pack(anchor=tk.W)
        
        stats_var = tk.BooleanVar(value=self.settings['show_stats'])
        ttk.Checkbutton(interface_frame, text="Показывать статистику", variable=stats_var).pack(anchor=tk.W)
        
        minimal_var = tk.BooleanVar(value=self.settings['minimal_mode'])
        ttk.Checkbutton(interface_frame, text="Минималистичный режим", variable=minimal_var).pack(anchor=tk.W)
        
        # Многоязычность
        multilang_var = tk.BooleanVar(value=self.settings['multilanguage'])
        ttk.Checkbutton(interface_frame, text="Поддержка разных раскладок", variable=multilang_var).pack(anchor=tk.W)
        
        # Сохраняем ссылки на переменные
        self.temp_settings_vars.update({
            'simulate_errors': errors_var,
            'error_rate': error_rate_var,
            'paragraph_pause': paragraph_var,
            'pause_duration': pause_var,
            'dark_theme': dark_var,
            'show_progress': progress_var,
            'show_stats': stats_var,
            'minimal_mode': minimal_var,
            'multilanguage': multilang_var
        })

    def setup_security_settings(self, parent):
        """Настраивает вкладку настроек безопасности"""
        # Автосохранение
        autosave_frame = ttk.Frame(parent)
        autosave_frame.pack(fill=tk.X, pady=5)
        
        autosave_var = tk.BooleanVar(value=self.settings['auto_save'])
        ttk.Checkbutton(autosave_frame, text="Автосохранение", variable=autosave_var).pack(side=tk.LEFT)
        
        # Шифрование
        encryption_frame = ttk.Frame(parent)
        encryption_frame.pack(fill=tk.X, pady=5)
        
        encryption_var = tk.BooleanVar(value=self.settings['encrypt_data'])
        ttk.Checkbutton(encryption_frame, text="Шифровать данные", variable=encryption_var).pack(side=tk.LEFT)
        
        # Автоочистка
        autoclear_frame = ttk.Frame(parent)
        autoclear_frame.pack(fill=tk.X, pady=5)
        
        autoclear_var = tk.BooleanVar(value=self.settings['auto_clear'])
        ttk.Checkbutton(autoclear_frame, text="Автоочистка текста", variable=autoclear_var).pack(side=tk.LEFT)
        
        ttk.Label(autoclear_frame, text="Через:").pack(side=tk.LEFT, padx=(20, 5))
        clear_delay_var = tk.StringVar(value=str(self.settings['clear_delay']))
        clear_delay_spin = ttk.Spinbox(autoclear_frame, from_=1, to=60, width=5, textvariable=clear_delay_var)
        clear_delay_spin.pack(side=tk.LEFT)
        ttk.Label(autoclear_frame, text="сек").pack(side=tk.LEFT, padx=5)
        
        # Системный трей
        tray_var = tk.BooleanVar(value=self.settings['use_tray'])
        ttk.Checkbutton(parent, text="Сворачивать в системный трей", variable=tray_var).pack(anchor=tk.W, pady=5)
        
        # Сохраняем ссылки на переменные
        self.temp_settings_vars.update({
            'auto_save': autosave_var,
            'encrypt_data': encryption_var,
            'auto_clear': autoclear_var,
            'clear_delay': clear_delay_var,
            'use_tray': tray_var
        })

    def save_all_settings(self, window):
        """Сохраняет все настройки"""
        # Сохраняем настройки из временных переменных
        for key, var in self.temp_settings_vars.items():
            if isinstance(var, tk.BooleanVar):
                self.settings[key] = var.get()
            else:
                try:
                    if key in ['typing_speed', 'speed_variation', 'error_rate', 'clear_delay']:
                        self.settings[key] = int(var.get())
                    elif key in ['pause_duration']:
                        self.settings[key] = float(var.get())
                    else:
                        self.settings[key] = var.get()
                except (ValueError, tk.TclError):
                    pass
        
        self.save_settings()
        self.setup_hotkeys()
        self.apply_theme()
        self.create_main_interface()
        
        window.destroy()
        messagebox.showinfo("Настройки", "Настройки сохранены успешно!")

    def import_text(self):
        """Импортирует текст из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, text)
                self.show_status(f"Текст импортирован из {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать файл: {str(e)}")

    def export_text(self):
        """Экспортирует текст в файл"""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "Нет текста для экспорта")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить текст как",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.show_status(f"Текст экспортирован в {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать файл: {str(e)}")

    def paste_from_clipboard(self):
        """Вставляет текст из буфера обмена"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.text_area.insert(tk.INSERT, clipboard_text)
            self.show_status("Текст вставлен из буфера обмена")
        except:
            messagebox.showerror("Ошибка", "Не удалось получить текст из буфера обмена")

    def show_history(self):
        """Показывает историю текстов"""
        history_window = tk.Toplevel(self.root)
        history_window.title("История текстов")
        history_window.geometry("500x400")
        
        ttk.Label(history_window, text="История ранее использованных текстов:").pack(anchor=tk.W, padx=10, pady=5)
        
        history_listbox = tk.Listbox(history_window)
        history_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for text in reversed(self.text_history):
            # Показываем первые 50 символов текста
            preview = text[:50] + "..." if len(text) > 50 else text
            history_listbox.insert(tk.END, preview)
        
        def load_selected_text():
            selection = history_listbox.curselection()
            if selection:
                index = len(self.text_history) - 1 - selection[0]
                selected_text = self.text_history[index]
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, selected_text)
                history_window.destroy()
        
        button_frame = ttk.Frame(history_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Загрузить выбранный", command=load_selected_text).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Закрыть", command=history_window.destroy).pack(side=tk.RIGHT, padx=5)

    def show_profiles(self):
        """Показывает управление профилями"""
        profiles_window = tk.Toplevel(self.root)
        profiles_window.title("Управление профилями")
        profiles_window.geometry("400x300")
        
        ttk.Label(profiles_window, text="Профили настроек:").pack(anchor=tk.W, padx=10, pady=5)
        
        profiles_listbox = tk.Listbox(profiles_window)
        profiles_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for profile_name in self.profiles.keys():
            profiles_listbox.insert(tk.END, profile_name)
        
        def save_current_profile():
            name = tk.simpledialog.askstring("Сохранение профиля", "Введите название профиля:")
            if name:
                self.profiles[name] = self.settings.copy()
                self.save_data()
                profiles_window.destroy()
                messagebox.showinfo("Успех", f"Профиль '{name}' сохранен")
        
        def load_selected_profile():
            selection = profiles_listbox.curselection()
            if selection:
                profile_name = profiles_listbox.get(selection[0])
                if profile_name in self.profiles:
                    self.settings.update(self.profiles[profile_name])
                    self.save_settings()
                    self.create_main_interface()
                    self.setup_hotkeys()
                    profiles_window.destroy()
                    messagebox.showinfo("Успех", f"Профиль '{profile_name}' загружен")
        
        def delete_selected_profile():
            selection = profiles_listbox.curselection()
            if selection:
                profile_name = profiles_listbox.get(selection[0])
                if messagebox.askyesno("Подтверждение", f"Удалить профиль '{profile_name}'?"):
                    del self.profiles[profile_name]
                    self.save_data()
                    profiles_window.destroy()
                    messagebox.showinfo("Успех", f"Профиль '{profile_name}' удален")
        
        button_frame = ttk.Frame(profiles_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Сохранить текущий", command=save_current_profile).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Загрузить выбранный", command=load_selected_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=delete_selected_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", command=profiles_window.destroy).pack(side=tk.RIGHT)

    def get_stats_text(self):
        """Возвращает текст статистики"""
        chars = self.stats['total_chars']
        time_sec = self.stats['total_time']
        sessions = self.stats['sessions']
        
        if time_sec > 0:
            speed = chars / (time_sec / 60)
        else:
            speed = 0
            
        return f"Символов: {chars}\nСессий: {sessions}\nСкорость: {speed:.1f} сим/мин"

    def update_stats_display(self):
        """Обновляет отображение статистики"""
        if self.settings['show_stats'] and hasattr(self, 'stats_label'):
            self.stats_label.config(text=self.get_stats_text())

    def apply_theme(self):
        """Применяет выбранную тему"""
        if self.settings['dark_theme']:
            # Простая темная тема
            style = ttk.Style()
            style.configure("TFrame", background="#2b2b2b")
            style.configure("TLabel", background="#2b2b2b", foreground="white")
            style.configure("TButton", background="#3c3c3c", foreground="white")
            style.configure("TEntry", fieldbackground="#3c3c3c", foreground="white")
            style.configure("TScrollbar", background="#3c3c3c")
        else:
            # Светлая тема по умолчанию
            style = ttk.Style()
            style.theme_use('clam')

    def toggle_minimal_mode(self):
        """Переключает минималистичный режим"""
        self.settings['minimal_mode'] = not self.settings['minimal_mode']
        self.create_main_interface()

    def setup_auto_save(self):
        """Настраивает автосохранение"""
        if self.settings['auto_save']:
            # Автосохранение каждые 30 секунд
            self.root.after(30000, self.auto_save)
    
    def auto_save(self):
        """Функция автосохранения"""
        if self.settings['auto_save']:
            self.save_data()
            # Планируем следующее автосохранение
            self.root.after(30000, self.auto_save)

    def show_help(self):
        help_text = """
Автоматический набор текста Pro - инструкция:

ОСНОВНОЕ ИСПОЛЬЗОВАНИЕ:
1. Введите текст в поле ввода или импортируйте из файла/буфера обмена
2. Настройте скорость и другие параметры
3. Нажмите "Запустить прослушивание"
4. Перейдите в нужное приложение и установите курсор
5. Нажмите горячую клавишу для начала набора

ГОРЯЧИЕ КЛАВИШИ:
- F6 (по умолчанию) - начать набор текста
- F7 (по умолчанию) - остановить набор

ОСНОВНЫЕ ФУНКЦИИ:
- Регулировка скорости набора
- Случайная скорость для естественности
- Имитация ошибок с автоматическим исправлением
- Паузы между абзацами
- История текстов и шаблоны
- Профили настроек
- Статистика набора
- Автосохранение и автоочистка

ВСЕ ФУНКЦИИ МОГУТ БЫТЬ ОТКЛЮЧЕНЫ В НАСТРОЙКАХ!
        """
        messagebox.showinfo("Справка", help_text)
        
    def on_closing(self):
        """Обработчик закрытия приложения"""
        self.stop_typing()
        
        # Сохраняем все данные
        self.save_settings()
        self.save_data()
        
        # Очищаем хоткеи
        if self.hotkey_listener:
            try:
                keyboard.remove_hotkey(self.hotkey_listener)
            except:
                pass
        if self.stop_hotkey_listener:
            try:
                keyboard.remove_hotkey(self.stop_hotkey_listener)
            except:
                pass
                
        self.root.destroy()

def main():
    try:
        import keyboard
        import pyautogui
        from cryptography.fernet import Fernet
    except ImportError as e:
        print(f"Установите необходимые библиотеки: {e}")
        print("pip install keyboard pyautogui cryptography")
        sys.exit(1)
        
    root = tk.Tk()
    app = TextTyperApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()