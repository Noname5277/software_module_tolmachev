import sqlite3
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import openpyxl  # Импортируем openpyxl для работы с Excel

class WarehouseManagementSystem:
    def __init__(self, parent):
        self.window = parent
        self.window.title("Система Управления Складом")
        self.window.geometry("800x500")

        # Подключение к базе данных
        self.conn = sqlite3.connect("warehouse.db")
        self.cursor = self.conn.cursor()
        self.initialize_database()

        # Инициализация интерфейса авторизации
        self.create_login_screen()

    def initialize_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                quantity INTEGER,
                price REAL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Inventory (
                id INTEGER PRIMARY KEY,
                name TEXT,
                quantity INTEGER,
                price REAL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Supplies (
                id INTEGER PRIMARY KEY,
                name TEXT,
                quantity INTEGER,
                price REAL,
                time TEXT
            )
        """)

        self.conn.commit()

    def create_login_screen(self):
        """Создает экран для авторизации и регистрации"""
        self.login_frame = ttk.Frame(self.window)
        self.login_frame.pack(expand=1)

        # Добавляем текстовый заголовок "Авторизация/Регистрация"
        ttk.Label(self.login_frame, text="Авторизация / Регистрация", font=("Arial", 16)).pack(pady=20)

        self.mode = 'login'  # Стартовый режим: авторизация

        ttk.Label(self.login_frame, text="Логин:").pack(pady=10)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text="Пароль:").pack(pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(self.login_frame, text="Авторизоваться", command=self.authenticate_user)
        self.login_button.pack(pady=10)

        self.register_button = ttk.Button(self.login_frame, text="Зарегистрироваться",
                                          command=self.show_registration_screen)
        self.register_button.pack(pady=10)

    def authenticate_user(self):
        """Проверка авторизации пользователя"""
        if self.mode == 'login':
            username = self.username_entry.get()
            password = self.password_entry.get()

            self.cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
            user = self.cursor.fetchone()

            if user:
                messagebox.showinfo("Успех", "Вы успешно авторизовались!")
                self.login_frame.destroy()  # Удаляем экран авторизации
                self.create_main_interface()  # Открываем основное приложение
            else:
                messagebox.showerror("Ошибка", "Неверный логин или пароль!")
        else:
            self.register_user()

    def show_registration_screen(self):
        """Переход в режим регистрации"""
        self.mode = 'register'
        self.login_button.config(text="Зарегистрироваться", command=self.authenticate_user)
        self.register_button.config(text="Назад", command=self.go_back_to_login)

    def register_user(self):
        """Регистрация нового пользователя"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
            return

        if len(password) < 8:
            messagebox.showerror("Ошибка", "Пароль должен содержать не менее 8 символов.")
            return

        self.cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        existing_user = self.cursor.fetchone()

        if existing_user:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
        else:
            self.cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
            self.mode = 'login'
            self.login_button.config(text="Авторизоваться", command=self.authenticate_user)
            self.register_button.config(text="Зарегистрироваться", command=self.show_registration_screen)

    def go_back_to_login(self):
        """Возвращаемся на экран авторизации"""
        self.mode = 'login'
        self.login_button.config(text="Авторизоваться", command=self.authenticate_user)
        self.register_button.config(text="Зарегистрироваться", command=self.show_registration_screen)

    def create_main_interface(self):
        """Создает основной интерфейс приложения"""
        self.window.geometry("800x500")  # Возвращаем прежний размер окна
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(expand=1, fill="both")

        self.create_product_management_tab()
        self.create_inventory_tab()
        self.create_supply_management_tab()

    def create_product_management_tab(self):
        self.product_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.product_tab, text='Управление Товарами')

        self.product_table = ttk.Treeview(self.product_tab, columns=("id", "name", "quantity", "price"),
                                          show="headings")
        self.product_table.heading("id", text="ID")
        self.product_table.heading("name", text="Название")
        self.product_table.heading("quantity", text="Количество")
        self.product_table.heading("price", text="Цена")
        self.product_table.pack(expand=1, fill="both")

        self.button_frame = ttk.Frame(self.product_tab)
        self.button_frame.pack(fill="x")
        ttk.Button(self.button_frame, text="Добавить товар", command=self.add_product).pack(side="left", padx=5, pady=5)
        ttk.Button(self.button_frame, text="Редактировать товар", command=self.edit_product).pack(side="left", padx=5,
                                                                                                  pady=5)
        ttk.Button(self.button_frame, text="Удалить товар", command=self.delete_product).pack(side="left", padx=5,
                                                                                              pady=5)
        ttk.Button(self.button_frame, text="Выгрузить в Excel", command=self.export_to_excel).pack(side="left", padx=5,
                                                                                                   pady=5)

        self.populate_products()

    def populate_products(self):
        self.product_table.delete(*self.product_table.get_children())
        self.cursor.execute("SELECT * FROM Products")
        for row in self.cursor.fetchall():
            self.product_table.insert('', 'end', values=row)

    def export_to_excel(self):
        try:
            # Создаем новый файл Excel
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Управление Товарами"

            # Добавляем заголовки столбцов
            sheet.append(["ID", "Название", "Количество", "Цена"])

            # Получаем данные из таблицы и записываем их в Excel
            self.cursor.execute("SELECT * FROM Products")
            for row in self.cursor.fetchall():
                sheet.append(row)

            # Сохраняем файл Excel
            file_path = "Products_Data.xlsx"
            workbook.save(file_path)

            messagebox.showinfo("Успех", f"Данные успешно экспортированы в файл: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при экспорте данных: {e}")

    def add_product(self):
        """Добавляет товар в управление товарами и запасы"""
        try:
            # Сбор данных от пользователя
            name = simpledialog.askstring("Добавить товар", "Введите название товара:")
            quantity = simpledialog.askinteger("Добавить товар", "Введите количество товара:")
            price = simpledialog.askfloat("Добавить товар", "Введите цену товара:")
            if name and quantity is not None and price is not None:
                # Добавляем в таблицу Products
                self.cursor.execute("INSERT INTO Products (name, quantity, price) VALUES (?, ?, ?)",
                                    (name, quantity, price))
                product_id = self.cursor.lastrowid  # Получаем ID добавленного товара

                # Добавляем в таблицу Inventory
                self.cursor.execute("INSERT INTO Inventory (id, name, quantity, price) VALUES (?, ?, ?, ?)",
                                    (product_id, name, quantity, price))
                self.conn.commit()

                # Обновление GUI
                self.populate_products()  # Обновляем управление товарами
                self.populate_inventory()  # Обновляем запасы
            else:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные!")

    def edit_product(self):
        selected_item = self.product_table.selection()
        if selected_item:
            item_values = self.product_table.item(selected_item, 'values')
            product_id = item_values[0]
            try:
                # Получаем новые значения от пользователя
                new_name = simpledialog.askstring("Редактировать товар", "Новое название:", initialvalue=item_values[1])
                new_quantity = simpledialog.askinteger("Редактировать товар", "Новое количество:",
                                                       initialvalue=item_values[2])
                new_price = simpledialog.askfloat("Редактировать товар", "Новая цена:", initialvalue=item_values[3])

                if new_name and new_quantity is not None and new_price is not None:
                    # Обновление данных в таблице Products
                    self.cursor.execute("UPDATE Products SET name = ?, quantity = ?, price = ? WHERE id = ?",
                                        (new_name, new_quantity, new_price, product_id))

                    # Обновление данных в таблице Inventory (отслеживание запасов)
                    self.cursor.execute("UPDATE Inventory SET name = ?, quantity = ?, price = ? WHERE id = ?",
                                        (new_name, new_quantity, new_price, product_id))

                    self.conn.commit()

                    # Обновление интерфейса
                    self.populate_products()  # Обновляем управление товарами
                    self.populate_inventory()  # Обновляем запасы
                else:
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные данные!")
        else:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования.")

    def delete_product(self):
        """Удаляет товар из управления товарами и запасов"""
        selected_item = self.product_table.selection()
        if selected_item:
            # Получаем ID удаляемого товара
            product_id = self.product_table.item(selected_item, 'values')[0]

            # Удаляем товар из таблицы Products
            self.cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))

            # Удаляем товар из таблицы Inventory
            self.cursor.execute("DELETE FROM Inventory WHERE id = ?", (product_id,))
            self.conn.commit()

            # Обновляем интерфейс
            self.populate_products()  # Обновляем таблицу товаров
            self.populate_inventory()  # Обновляем таблицу запасов
        else:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления.")

    def create_inventory_tab(self):
        self.inventory_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.inventory_tab, text='Отслеживание Запасов')

        # Таблица для отображения товаров
        self.inventory_table = ttk.Treeview(self.inventory_tab, columns=("id", "name", "quantity", "price"),
                                            show="headings")
        self.inventory_table.heading("id", text="ID")
        self.inventory_table.heading("name", text="Название")
        self.inventory_table.heading("quantity", text="Количество")
        self.inventory_table.heading("price", text="Цена")
        self.inventory_table.pack(expand=1, fill="both")

        # Рамка для фильтров и поиска
        self.control_frame = ttk.Frame(self.inventory_tab)
        self.control_frame.pack(fill="x", padx=10, pady=10)

        # Кнопка фильтрации (заглушка)
        self.filter_button = ttk.Button(self.control_frame, text="Фильтровать", command=self.dummy_filter)
        self.filter_button.pack(side="top", pady=5)

        # Поле ввода для поиска и кнопка поиска
        self.search_frame = ttk.Frame(self.control_frame)
        self.search_frame.pack(fill="x", pady=10)

        self.search_entry = ttk.Entry(self.search_frame)  # Поле для поиска
        self.search_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        ttk.Button(self.search_frame, text="Поиск", command=self.search_inventory).pack(side="left")

        # Заполняем таблицу запасов
        self.populate_inventory()

    def dummy_filter(self):
        """Заглушка для кнопки фильтрации (не выполняет никаких действий)"""
        messagebox.showinfo("Информация", "Эта кнопка пока не работает!")

    def populate_inventory(self):
        self.inventory_table.delete(*self.inventory_table.get_children())
        self.cursor.execute("SELECT * FROM Inventory")
        for row in self.cursor.fetchall():
            self.inventory_table.insert('', 'end', values=row)

    def search_inventory(self):
        search_query = self.search_entry.get().strip()
        self.inventory_table.delete(*self.inventory_table.get_children())
        if search_query:
            self.cursor.execute("SELECT * FROM Inventory WHERE name LIKE ?", (f"%{search_query}%",))
        else:
            self.cursor.execute("SELECT * FROM Inventory")
        for row in self.cursor.fetchall():
            self.inventory_table.insert('', 'end', values=row)

    def create_supply_management_tab(self):
        self.supply_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.supply_tab, text='Управление Поставками')

        self.order_table = ttk.Treeview(self.supply_tab, columns=("id", "name", "quantity", "price", "time"),
                                        show="headings")
        self.order_table.heading("id", text="ID")
        self.order_table.heading("name", text="Название")
        self.order_table.heading("quantity", text="Количество")
        self.order_table.heading("price", text="Цена")
        self.order_table.heading("time", text="Время доставки")
        self.order_table.pack(expand=1, fill="both")

        ttk.Button(self.supply_tab, text="Заказать товар", command=self.order_product).pack(side="top", padx=10,
                                                                                            pady=10)

        # Загрузка заказов из базы данных
        self.populate_supplies()

    def order_product(self):
        """Создает заказ и запускает его обработку"""
        try:
            # Сбор данных о заказе
            name = simpledialog.askstring("Заказать товар", "Введите название товара:")
            quantity = simpledialog.askinteger("Заказать товар", "Введите количество товара:")
            price = simpledialog.askfloat("Заказать товар", "Введите цену товара:")

            if name and quantity is not None and price is not None:
                # Добавляем заказ в таблицу Supplies (заказы)
                self.cursor.execute("INSERT INTO Supplies (name, quantity, price, time) VALUES (?, ?, ?, ?)",
                                    (name, quantity, price, "10 секунд"))
                self.conn.commit()

                # Обновление интерфейса (отображение новых заказов)
                self.populate_supplies()

                # Запускаем обработку заказа в отдельном потоке (с таймером)
                threading.Thread(target=self.process_order, args=(self.cursor.lastrowid, name, quantity, price),
                                 daemon=True).start()
            else:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные данные!")

    def populate_supplies(self):
        """Загружает заказы из базы данных в таблицу управления поставками"""
        self.order_table.delete(*self.order_table.get_children())
        self.cursor.execute("SELECT id, name, quantity, price, time FROM Supplies")
        for row in self.cursor.fetchall():
            self.order_table.insert('', 'end', values=row)

    def process_order(self, order_id, name, quantity, price):
        """Эмулирует обработку заказа с таймером"""
        for i in range(10, 0, -1):
            self.window.after(i * 1000, self.update_timer, order_id, i)

        # После истечения времени добавляем товар в таблицы
        self.window.after(10 * 1000, lambda: self.complete_order(order_id, name, quantity, price))

    def update_timer(self, order_id, remaining_time):
        """Обновляет таймер в таблице заказов"""
        for item in self.order_table.get_children():
            item_values = self.order_table.item(item, "values")
            if item_values[0] == order_id:
                self.order_table.item(item, values=(item_values[0], item_values[1], item_values[2],
                                                    item_values[3], f"{remaining_time} секунд"))

    def remove_order_from_table(self, order_id):
        """Удаляет заказ из таблицы заказов в GUI"""
        for item in self.order_table.get_children():
            item_values = self.order_table.item(item, "values")
            if item_values[0] == order_id:
                self.order_table.delete(item)
                break

    def close_application(self):
        """Закрытие приложения и сохранение изменений в базе данных"""
        self.conn.close()
        self.window.quit()  # Завершаем работу программы

    def complete_order(self, order_id, name, quantity, price):
        """Добавляет товар в инвентарь и обновляет управление товарами"""
        # Обновление запасов (Inventory)
        self.cursor.execute("INSERT INTO Inventory (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))

        # Добавление товара в таблицу Products (управление товарами)
        self.cursor.execute("INSERT INTO Products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
        self.conn.commit()

        # Обновление GUI
        self.populate_inventory()
        self.populate_products()

        # Помечаем заказ как обработанный в GUI
        for item in self.order_table.get_children():
            item_values = self.order_table.item(item, "values")
            if item_values[0] == order_id:
                self.order_table.item(item, tags=("processed",))
                break

        # Настроим стили для обработанных заказов
        self.order_table.tag_configure("processed", background="lightgreen")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseManagementSystem(root)
    root.protocol("WM_DELETE_WINDOW", app.close_application)  # Обработка закрытия окна
    root.mainloop()
