import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import pyautogui
import sys
import random

class TextTyperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматический набор текста")
        self.root.geometry("770x600")
        self.root.resizable(True, True)
        
        # Переменные
        self.hotkey = "F6"
        self.stop_hotkey = "F7"
        self.typing_speed = 200  # символов в минуту
        self.is_listening = False
        self.is_typing = False
        self.hotkey_listener = None
        self.stop_hotkey_listener = None
        self.use_random_speed = tk.BooleanVar(value=True)
        self.speed_variation = tk.IntVar(value=15)
        
        self.create_widgets()
        self.setup_hotkeys()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Верхняя панель с кнопкой справки
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Кнопка справки с иконкой
        help_btn = ttk.Button(top_frame, text="?", width=2, command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        # Заголовок
        title_label = ttk.Label(top_frame, text="Автоматический набор текста", font=("Arial", 12, "bold"))
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        top_frame.columnconfigure(1, weight=1)
        
        # Поле для ввода текста
        ttk.Label(main_frame, text="Текст для ввода:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.text_area = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.text_area.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar для текстового поля
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # Прогресс-бар
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(progress_frame, text="Прогресс:").grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=2, sticky=tk.W)
        
        progress_frame.columnconfigure(1, weight=1)
        
        # Настройки скорости
        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(settings_frame, text="Скорость набора:").grid(row=0, column=0, sticky=tk.W)
        
        self.speed_var = tk.StringVar(value="200")
        speed_scale = ttk.Scale(settings_frame, from_=10, to=400, orient=tk.HORIZONTAL,
                               variable=self.speed_var, command=self.on_speed_change)
        speed_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10))
        
        self.speed_label = ttk.Label(settings_frame, text="200 символов/мин")
        self.speed_label.grid(row=0, column=2, sticky=tk.W)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Настройки случайной скорости
        random_speed_frame = ttk.Frame(main_frame)
        random_speed_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.random_check = ttk.Checkbutton(random_speed_frame, text="Случайная скорость", 
                                           variable=self.use_random_speed)
        self.random_check.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(random_speed_frame, text="Разброс скорости:").grid(row=0, column=1, sticky=tk.W, padx=(20, 5))
        
        variation_spin = ttk.Spinbox(random_speed_frame, from_=1, to=20, width=5,
                                    textvariable=self.speed_variation)
        variation_spin.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        
        ttk.Label(random_speed_frame, text="символов/мин").grid(row=0, column=3, sticky=tk.W)
        
        # Настройки горячих клавиш
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Горячая клавиша запуска
        ttk.Label(hotkey_frame, text="Горячая клавиша:").grid(row=0, column=0, sticky=tk.W)
        
        self.hotkey_var = tk.StringVar(value="F8")
        hotkey_combo = ttk.Combobox(hotkey_frame, textvariable=self.hotkey_var, 
                                   values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                   state="readonly", width=10)
        hotkey_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        hotkey_combo.bind('<<ComboboxSelected>>', self.on_hotkey_change)
        
        # Горячая клавиша остановки
        ttk.Label(hotkey_frame, text="Стоп клавиша:").grid(row=0, column=2, sticky=tk.W)
        
        self.stop_hotkey_var = tk.StringVar(value="F9")
        stop_hotkey_combo = ttk.Combobox(hotkey_frame, textvariable=self.stop_hotkey_var, 
                                        values=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
                                        state="readonly", width=10)
        stop_hotkey_combo.grid(row=0, column=3, sticky=tk.W, padx=(10, 10))
        stop_hotkey_combo.bind('<<ComboboxSelected>>', self.on_stop_hotkey_change)
        
        self.status_label = ttk.Label(hotkey_frame, text="Горячие клавиши активны", foreground="green")
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Запустить прослушивание", command=self.toggle_listening)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Остановить набор", command=self.stop_typing, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="Тестировать набор", command=self.test_typing).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Очистить текст", command=self.clear_text).grid(row=0, column=3, padx=(0, 10))
        
        # Индикатор состояния
        state_frame = ttk.Frame(main_frame)
        state_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.state_indicator = ttk.Label(state_frame, text="⏹️ Не печатает", foreground="red")
        self.state_indicator.grid(row=0, column=0, sticky=tk.W)
        
        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
    def on_speed_change(self, value):
        speed = int(float(value))
        self.typing_speed = speed
        self.speed_label.config(text=f"{speed} символов/мин")
        
    def on_hotkey_change(self, event=None):
        new_hotkey = self.hotkey_var.get()
        if new_hotkey != self.hotkey:
            self.setup_hotkeys()
            
    def on_stop_hotkey_change(self, event=None):
        new_hotkey = self.stop_hotkey_var.get()
        if new_hotkey != self.stop_hotkey:
            self.setup_hotkeys()
            
    def setup_hotkeys(self):
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
        
        self.hotkey = self.hotkey_var.get()
        self.stop_hotkey = self.stop_hotkey_var.get()
        
        try:
            self.hotkey_listener = keyboard.add_hotkey(self.hotkey, self.on_hotkey_pressed)
            self.stop_hotkey_listener = keyboard.add_hotkey(self.stop_hotkey, self.on_stop_hotkey_pressed)
            self.status_label.config(text=f"Горячие клавиши активны: {self.hotkey} - старт, {self.stop_hotkey} - стоп", foreground="green")
            self.status_var.set(f"Горячие клавиши настроены: {self.hotkey} для старта, {self.stop_hotkey} для остановки")
        except Exception as e:
            self.status_label.config(text="Ошибка настройки горячих клавиш", foreground="red")
            self.status_var.set(f"Ошибка: {str(e)}")
            
    def on_hotkey_pressed(self):
        if self.is_listening and not self.is_typing:
            text_to_type = self.text_area.get("1.0", tk.END).strip()
            if text_to_type:
                # Запускаем в отдельном потоке чтобы не блокировать GUI
                thread = threading.Thread(target=self.type_text, args=(text_to_type,))
                thread.daemon = True
                thread.start()
            else:
                self.status_var.set("Ошибка: нет текста для ввода")
                
    def on_stop_hotkey_pressed(self):
        self.stop_typing()
            
    def stop_typing(self):
        if self.is_typing:
            self.is_typing = False
            self.status_var.set("Набор текста остановлен")
            self.update_state_indicator()
            
    def type_text(self, text):
        try:
            self.is_typing = True
            self.update_state_indicator()
            
            # Сбрасываем прогресс
            self.progress_var.set(0)
            self.progress_label.config(text="0%")
            
            # Небольшая задержка перед началом набора
            time.sleep(0.5)
            
            total_chars = len(text)
            typed_chars = 0
            
            for char in text:
                if not self.is_typing:
                    break
                    
                pyautogui.write(char)
                
                # Рассчитываем задержку между символами
                if self.use_random_speed.get():
                    # Случайная скорость в пределах указанного разброса
                    current_speed = self.typing_speed + random.randint(-self.speed_variation.get(), self.speed_variation.get())
                    current_speed = max(10, current_speed)  # Минимум 10 символов в минуту
                else:
                    current_speed = self.typing_speed
                    
                delay_per_char = 60.0 / current_speed
                
                # Добавляем небольшую случайную вариацию к задержке для естественности
                variation = random.uniform(0.8, 1.2)
                time.sleep(delay_per_char * variation)
                
                # Обновляем прогресс
                typed_chars += 1
                progress = (typed_chars / total_chars) * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"{int(progress)}%")
                
            if self.is_typing:
                self.status_var.set("Текст успешно введен")
                self.progress_var.set(100)
                self.progress_label.config(text="100%")
            else:
                self.status_var.set("Набор текста прерван")
                
            self.is_typing = False
            self.update_state_indicator()
            
        except Exception as e:
            self.status_var.set(f"Ошибка при вводе текста: {str(e)}")
            self.is_typing = False
            self.update_state_indicator()
            
    def update_state_indicator(self):
        if self.is_typing:
            self.state_indicator.config(text="🟢 Печатает...", foreground="green")
            self.stop_button.config(state="normal")
        else:
            self.state_indicator.config(text="⏹️ Не печатает", foreground="red")
            self.stop_button.config(state="disabled")
            
    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.start_button.config(text="Остановить прослушивание")
            self.status_var.set(f"Прослушивание активно. Нажмите {self.hotkey} для ввода текста, {self.stop_hotkey} для остановки")
        else:
            self.start_button.config(text="Запустить прослушивание")
            self.status_var.set("Прослушивание остановлено")
            
    def test_typing(self):
        text_to_type = self.text_area.get("1.0", tk.END).strip()
        if text_to_type:
            self.status_var.set("Тестирование набора...")
            thread = threading.Thread(target=self.type_text, args=(text_to_type,))
            thread.daemon = True
            thread.start()
        else:
            messagebox.showwarning("Предупреждение", "Введите текст для тестирования")
            
    def clear_text(self):
        self.text_area.delete("1.0", tk.END)
        self.status_var.set("Текст очищен")
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        
    def show_help(self):
        help_text = """
ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:

1. Введите текст в поле для ввода
2. Настройте скорость набора (символов в минуту)
3. Включите "Случайная скорость" для естественности (опционально)
4. Выберите горячие клавиши для старта и остановки
5. Нажмите "Запустить прослушивание"
6. Перейдите в нужное приложение и установите курсор
7. Нажмите стартовую горячую клавишу для начала ввода
8. Нажмите стоп-клавишу для прерывания ввода в любой момент

ФУНКЦИИ:
- Случайная скорость: добавляет естественные вариации в скорость набора
- Стоп-клавиша: мгновенно останавливает набор текста
- Тестирование: проверка работы без активации горячих клавиш
- Индикатор состояния: показывает, идет ли в данный момент набор
- Прогресс-бар: отображает прогресс набора текста

ПРИМЕЧАНИЕ: Убедитесь, что у программы есть права на запись в системе.
        """
        messagebox.showinfo("Справка", help_text)
        
    def on_closing(self):
        # Останавливаем набор если активен
        self.stop_typing()
        
        # Очищаем хоткеи при закрытии
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
    # Проверяем зависимости
    try:
        import keyboard
        import pyautogui
    except ImportError:
        print("Установите необходимые библиотеки:")
        print("pip install keyboard pyautogui")
        sys.exit(1)
        
    root = tk.Tk()
    app = TextTyperApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()