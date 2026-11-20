import webbrowser
from urllib.parse import quote
from pathlib import Path
from datetime import date, datetime
import re

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps, ImageEnhance

from app.database.cloud_db import CloudDatabase
from auth import get_current_user
from auth_window import AuthWindow


# =========================================================
# НАСТРОЙКИ И ЦВЕТА
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

BG = "#171717"
SIDE = "#202020"
CARD = "#252525"
CARD2 = "#303030"
BEIGE = "#E7C69F"
BEIGE_HOVER = "#D6B58F"
TEXT = "#F4EEE7"
MUTED = "#B8ADA2"
GREEN = "#82B878"
RED = "#D77968"

MAX_CARS = 3


# =========================================================
# МАРКИ И МОДЕЛИ
# =========================================================

BRANDS = {
    "Opel": ["Astra", "Corsa", "Insignia", "Vectra", "Zafira"],
    "LADA": ["Granta", "Vesta", "Niva", "Kalina", "Priora"],
    "Toyota": ["Camry", "Corolla", "RAV4", "Land Cruiser", "Yaris"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "1 Series"],
    "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC", "GLE"],
    "Audi": ["A3", "A4", "A6", "Q5", "Q7"],
    "Volkswagen": ["Polo", "Golf", "Passat", "Tiguan", "Touareg"],
    "Kia": ["Rio", "Ceed", "Sportage", "Sorento", "K5"],
    "Hyundai": ["Solaris", "Elantra", "Tucson", "Santa Fe", "Creta"],
    "Nissan": ["Almera", "Qashqai", "X-Trail", "Juke", "Teana"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Jazz"],
    "Ford": ["Focus", "Mondeo", "Kuga", "Fiesta", "Explorer"],
    "Renault": ["Logan", "Sandero", "Duster", "Arkana", "Kaptur"],
    "Chevrolet": ["Cruze", "Lacetti", "Aveo", "Captiva", "Tahoe"],
    "Skoda": ["Octavia", "Rapid", "Superb", "Kodiaq", "Fabia"]
}


# =========================================================
# ВИДЫ ОБСЛУЖИВАНИЯ
# =========================================================

SERVICES = [
    "Замена моторного масла",
    "Замена масляного фильтра",
    "Замена воздушного фильтра",
    "Замена салонного фильтра",
    "Замена топливного фильтра",
    "Замена свечей зажигания",
    "Замена тормозных колодок",
    "Замена тормозной жидкости",
    "Замена охлаждающей жидкости",
    "Замена антифриза",
    "Замена ремня ГРМ",
    "Замена цепи ГРМ",
    "Замена аккумулятора",
    "Замена шин",
    "Техническое обслуживание",
    "Другое"
]


# =========================================================
# ПЕРЕВОДЫ
# =========================================================

LANGUAGE_FILE = Path(__file__).resolve().parent / "language.txt"


def load_language():
    try:
        language = LANGUAGE_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if language in ("ru", "en"):
            return language

    except (FileNotFoundError, OSError):
        pass

    return "ru"


CURRENT_LANGUAGE = load_language()


TRANSLATIONS = {
    "Главная": "Home",
    "Мой гараж": "My Garage",
    "Обслуживание": "Maintenance",
    "Болячки": "Common Issues",
    "Напоминания": "Reminders",
    "Автосервис": "Car Services",
    "Настройки": "Settings",

    "ВАШ АВТОМОБИЛЬНЫЙ ПОМОЩНИК": "YOUR PERSONAL CAR ASSISTANT",
    "Ваш автомобиль и ближайшие напоминания": "Your car and upcoming reminders",

    "Добро пожаловать в Lapka Motors": "Welcome to Lapka Motors",
    "Добавьте первый автомобиль — здесь появятся пробег, обслуживание и напоминания.": "Add your first car to see mileage, maintenance and reminders.",

    "＋ Добавить автомобиль": "＋ Add Vehicle",
    "Добавить автомобиль": "Add Vehicle",
    "Сохранить автомобиль": "Save Vehicle",
    "Сохранить изменения": "Save Changes",

    "Редактировать автомобиль": "Edit Vehicle",
    "Профиль автомобиля": "Vehicle Profile",
    "Подробная информация о вашем автомобиле": "Detailed information about your vehicle",

    "← Назад в гараж": "← Back to Garage",

    "Ближайшие напоминания": "Upcoming Reminders",
    "Ближайшие напоминания по датам и пробегу": "Upcoming reminders by date and mileage",

    "Быстрые действия": "Quick Actions",
    "＋ Добавить запись": "＋ Add Record",

    "История обслуживания": "Maintenance History",

    "Пока всё спокойно": "Everything is up to date",

    "Добавьте обслуживание, и Lapka Motors напомнит,\nкогда придёт время повторить процедуру.": "Add a maintenance record and Lapka Motors will remind you when it is time to repeat the procedure.",

    "＋ Добавить обслуживание": "＋ Add Maintenance",

    "Ваша коллекция автомобилей": "Your vehicle collection",
    "Гараж пока пуст": "Your garage is empty",
    "Добавьте первый автомобиль в Lapka Motors.": "Add your first vehicle to Lapka Motors.",

    "АВТОМОБИЛИ": "VEHICLES",
    "● ВЫБРАННЫЙ АВТОМОБИЛЬ": "● SELECTED VEHICLE",

    "Выбрано": "Selected",
    "Выбрать": "Select",
    "Профиль": "Profile",
    "Пробег": "Mileage",
    "Изменить": "Edit",
    "Удалить": "Delete",

    "ПРОБЕГ": "MILEAGE",
    "ГОД": "YEAR",
    "МАРКА": "BRAND",
    "МОДЕЛЬ": "MODEL",
    "ГОД ВЫПУСКА": "YEAR",
    "ТЕКУЩИЙ ПРОБЕГ": "CURRENT MILEAGE",
    "ТРЕБУЮТ ВНИМАНИЯ": "NEEDS ATTENTION",

    "Не указан": "Not specified",

    "ФОТОГРАФИЯ АВТОМОБИЛЯ\nСКОРО ПОЯВИТСЯ": "VEHICLE PHOTO\nCOMING SOON",

    "Болячки автомобиля": "Common Vehicle Issues",
    "Узнайте о типичных неисправностях вашей модели": "Learn about common problems with your vehicle model",

    "Нет автомобиля": "No vehicle found",
    "Сначала добавьте автомобиль в гараж.": "Add a vehicle to your garage first.",

    "Типичные неисправности": "Common Issues",

    "Здесь вы сможете изучить распространённые проблемы вашего автомобиля, узнать о слабых местах модели и почитать отзывы владельцев.": "Here you can explore common problems, learn about weak points of your model and read owner reviews.",

    "Изучить болячки на Drom": "Explore Issues on Drom",
    "Другие источники": "Other Sources",

    "Найдите подходящий сервис для вашего автомобиля": "Find the right service for your vehicle",

    "Добавьте машину в гараж, чтобы продолжить.": "Add a vehicle to your garage to continue.",

    "ВЫБЕРИТЕ УСЛУГУ": "CHOOSE A SERVICE",

    "Автосервисы": "Auto Repair Shops",
    "Ремонт и обслуживание": "Repair and maintenance",

    "Шиномонтаж": "Tire Service",
    "Замена и ремонт шин": "Tire replacement and repair",

    "Автомойки": "Car Washes",
    "Мойка и уход за кузовом": "Car washing and body care",

    "Диагностика": "Diagnostics",
    "Компьютерная диагностика": "Computer diagnostics",

    "Найти на карте": "Find on Map",

    "История работ по всем автомобилям": "Service history for all vehicles",

    "Новая запись": "New Record",
    "Добавить запись": "Add Record",

    "Сроки обслуживания по датам и пробегу": "Maintenance due dates and mileage",

    "Нет автомобилей": "No vehicles",
    "Сначала добавьте машину в гараж.": "Add a vehicle to your garage first.",

    "Нет процедур с заданными интервалами.": "No maintenance intervals have been set.",

    "Параметры приложения Lapka Motors": "Lapka Motors application settings",

    "Оформление": "Appearance",
    "Тёмная тема, графитовые карточки и бежевые акценты.": "Dark theme, graphite cards and beige accents.",

    "Хранение данных": "Data Storage",
    "Язык приложения": "Application Language",
    "Выберите язык интерфейса": "Choose the interface language",

    "Русский": "Russian",
    "English": "English",

    "Марка": "Brand",
    "Модель": "Model",
    "Год выпуска": "Year",
    "Год выпуска (необязательно)": "Year (optional)",
    "Текущий пробег, км": "Current mileage, km",

    "Процедура": "Service",
    "Автомобиль": "Vehicle",
    "Дата (ДД.ММ.ГГГГ)": "Date (DD.MM.YYYY)",
    "Пробег при обслуживании, км": "Mileage at service, km",
    "Интервал в днях (0 — отключить)": "Interval in days (0 — disabled)",
    "Интервал в километрах (0 — отключить)": "Interval in km (0 — disabled)",
    "Комментарий": "Comment",

    "Сохранить запись": "Save Record",

    "Удаление": "Delete",
    "Удалить запись обслуживания?": "Delete this maintenance record?",

    "Ошибка": "Error",
    "Проверьте год и пробег.": "Check the year and mileage.",
    "Проверьте дату и числовые значения.": "Check the date and numeric values.",

    "Удалить автомобиль": "Delete Vehicle",
    "Изменить пробег": "Change Mileage"
}


def translate(value):
    if not isinstance(value, str):
        return value

    if CURRENT_LANGUAGE == "en":
        return TRANSLATIONS.get(value, value)

    return value


# Перевод подписей при создании элементов интерфейса.
_original_label = ctk.CTkLabel
_original_button = ctk.CTkButton


def translated_label(*args, **kwargs):
    if "text" in kwargs:
        kwargs["text"] = translate(kwargs["text"])

    return _original_label(*args, **kwargs)


def translated_button(*args, **kwargs):
    if "text" in kwargs:
        text = kwargs["text"]

        if isinstance(text, str):
            for icon in ("⌂", "▣", "⚒", "⚠", "◷", "🔧", "⚙"):
                prefix = f"{icon}    "

                if text.startswith(prefix):
                    text = prefix + translate(text[len(prefix):])
                    break

        kwargs["text"] = translate(text)

    return _original_button(*args, **kwargs)


ctk.CTkLabel = translated_label
ctk.CTkButton = translated_button


# =========================================================
# ОСНОВНОЙ КЛАСС
# =========================================================

class LapkaApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Lapka Motors")
        self.geometry("1220x790")
        self.minsize(1000, 680)
        self.configure(fg_color=BG)

        # Иконка приложения
        icon_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "images"
            / "lapka.ico"
        )

        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception as error:
                print("Не удалось установить иконку:", error)

        self.db = CloudDatabase()

        self.selected_id = None
        self.current_page = "Главная"

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------
        # БОКОВАЯ ПАНЕЛЬ
        # -------------------------------------------------

        self.sidebar = ctk.CTkFrame(
            self,
            width=225,
            corner_radius=0,
            fg_color="#000000"
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        # Логотип
        logo_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "images"
            / "lapka_logo.png"
        )

        if logo_path.exists():

            try:
                with Image.open(logo_path) as source_image:
                    logo_file = source_image.convert("RGB")

                    width, height = logo_file.size

                    logo_file = logo_file.crop((
                        int(width * 0.05),
                        int(height * 0.25),
                        int(width * 0.95),
                        int(height * 0.65)
                    ))

                self.logo_image = ctk.CTkImage(
                    light_image=logo_file,
                    dark_image=logo_file,
                    size=(195, 43)
                )

                ctk.CTkLabel(
                    self.sidebar,
                    text="",
                    image=self.logo_image,
                    fg_color="transparent"
                ).pack(
                    padx=10,
                    pady=(25, 5)
                )

            except Exception as error:
                print("Не удалось загрузить логотип:", error)
                self._show_text_logo()

        else:
            self._show_text_logo()

        ctk.CTkLabel(
            self.sidebar,
            text="ВАШ АВТОМОБИЛЬНЫЙ ПОМОЩНИК",
            text_color=MUTED,
            font=ctk.CTkFont(
                "Segoe UI",
                8,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=26,
            pady=(0, 35)
        )

        # Навигация
        self.nav = {}

        navigation = [
            ("Главная", "⌂"),
            ("Мой гараж", "▣"),
            ("Обслуживание", "⚒"),
            ("Болячки", "⚠"),
            ("Напоминания", "◷"),
            ("Автосервис", "🔧"),
            ("Настройки", "⚙")
        ]

        for name, icon in navigation:

            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}    {name}",
                anchor="w",
                height=45,
                corner_radius=10,
                fg_color="transparent",
                hover_color=CARD2,
                text_color=TEXT,
                font=ctk.CTkFont(
                    "Segoe UI",
                    13
                ),
                command=lambda n=name: self.show(n)
            )

            button.pack(
                fill="x",
                padx=14,
                pady=4
            )

            self.nav[name] = button

        ctk.CTkLabel(
            self.sidebar,
            text="LAPKA MOTORS  for  DESKTOP",
            text_color="#776E65",
            font=ctk.CTkFont(
                "Segoe UI",
                9
            )
        ).pack(
            side="bottom",
            anchor="w",
            padx=22,
            pady=22
        )

        # -------------------------------------------------
        # ОСНОВНАЯ РАБОЧАЯ ОБЛАСТЬ
        # -------------------------------------------------

        self.area = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0
        )

        self.area.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=28,
            pady=22
        )

        cars = self.db.cars()

        if cars:
            self.selected_id = cars[0]["id"]

        self.show("Главная")

    def _show_text_logo(self):
        ctk.CTkLabel(
            self.sidebar,
            text="LAPKA MOTORS",
            text_color=BEIGE,
            font=ctk.CTkFont(
                "Segoe UI",
                22,
                "bold"
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(32, 5)
        )

    # =====================================================
    # НАВИГАЦИЯ
    # =====================================================

    def clear(self):
        for widget in self.area.winfo_children():
            widget.destroy()

    def show(self, page):

        self.current_page = page

        for name, button in self.nav.items():

            active = name == page

            button.configure(
                fg_color=BEIGE if active else "transparent",
                text_color="#211A14" if active else TEXT,
                text=self._navigation_text(name)
            )

        self.clear()

        pages = {
            "Главная": self.home,
            "Мой гараж": self.garage,
            "Болячки": self.ailments,
            "Обслуживание": self.service,
            "Напоминания": self.reminders,
            "Автосервис": self.auto_service,
            "Настройки": self.settings
        }

        page_function = pages.get(page, self.home)
        page_function()

    def _navigation_text(self, name):

        icons = {
            "Главная": "⌂",
            "Мой гараж": "▣",
            "Обслуживание": "⚒",
            "Болячки": "⚠",
            "Напоминания": "◷",
            "Автосервис": "🔧",
            "Настройки": "⚙"
        }

        return f"{icons[name]}    {translate(name)}"

    # =====================================================
    # ВСПОМОГАТЕЛЬНЫЕ ЭЛЕМЕНТЫ
    # =====================================================

    def heading(self, title, subtitle):

        ctk.CTkLabel(
            self.area,
            text=title,
            text_color=TEXT,
            font=ctk.CTkFont(
                "Segoe UI",
                28,
                "bold"
            )
        ).pack(
            anchor="w",
            pady=(8, 3)
        )

        ctk.CTkLabel(
            self.area,
            text=subtitle,
            text_color=MUTED,
            font=ctk.CTkFont(
                "Segoe UI",
                12
            )
        ).pack(
            anchor="w",
            pady=(0, 20)
        )

    def card(self, parent=None, width=None):

        options = {
            "fg_color": CARD,
            "corner_radius": 17
        }

        if width is not None:
            options["width"] = width

        return ctk.CTkFrame(
            parent if parent is not None else self.area,
            **options
        )

    def primary(self, parent, text, command, width=190):

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=42,
            corner_radius=11,
            fg_color=BEIGE,
            hover_color=BEIGE_HOVER,
            text_color="#211A14",
            font=ctk.CTkFont(
                "Segoe UI",
                12,
                "bold"
            )
        )

    def secondary(self, parent, text, command, width=130):

        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=38,
            corner_radius=10,
            fg_color="#111111",
            hover_color="#30251B",
            text_color="#E7C69F",
            border_width=1,
            border_color="#5A4632",
            font=ctk.CTkFont(
                "Segoe UI",
                12
            )
        )

    def empty(
        self,
        title,
        subtitle,
        command,
        button="＋ Добавить автомобиль"
    ):

        panel = self.card()
        panel.pack(
            fill="x",
            pady=22
        )

        ctk.CTkLabel(
            panel,
            text=title,
            text_color=TEXT,
            font=ctk.CTkFont(
                size=19,
                weight="bold"
            )
        ).pack(pady=(28, 8))

        ctk.CTkLabel(
            panel,
            text=subtitle,
            text_color=MUTED,
            wraplength=600
        ).pack(pady=4)

        self.primary(
            panel,
            button,
            command
        ).pack(pady=(18, 28))

    # =====================================================
    # ГЛАВНАЯ СТРАНИЦА
    # =====================================================

    def home(self):

        self.heading(
            "Главная",
            "Ваш автомобиль и ближайшие напоминания"
        )

        cars = self.db.cars()

        if not cars:

            self.empty(
                "Добро пожаловать в Lapka Motors",
                "Добавьте первый автомобиль — здесь появятся пробег, обслуживание и напоминания.",
                self.add_car
            )

            return

        car = next(
            (
                item for item in cars
                if item["id"] == self.selected_id
            ),
            cars[0]
        )

        self.selected_id = car["id"]

        hero = ctk.CTkFrame(
            self.area,
            fg_color="#000000",
            corner_radius=19
        )

        hero.pack(
            fill="x",
            pady=(0, 16)
        )

        top = ctk.CTkFrame(
            hero,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            padx=22,
            pady=(20, 8)
        )

        ctk.CTkLabel(
            top,
            text=f"{car['brand']} {car['model']}",
            text_color=TEXT,
            font=ctk.CTkFont(
                "Segoe UI",
                25,
                "bold"
            )
        ).pack(side="left")

        menu = ctk.CTkOptionMenu(
            top,
            values=[
                f"{item['id']} | {item['brand']} {item['model']}"
                for item in cars
            ],
            command=self.select_car,
            fg_color="#000000",
            button_color="#30251B",
            button_hover_color="#51402E",
            text_color="#E7C69F",
            dropdown_fg_color="#000000",
            dropdown_hover_color="#30251B",
            dropdown_text_color="#E7C69F",
            corner_radius=12,
            width=245,
            height=38
        )

        menu.set(
            f"{car['id']} | {car['brand']} {car['model']}"
        )

        menu.pack(side="right")

        content = ctk.CTkFrame(
            hero,
            fg_color="transparent"
        )

        content.pack(
            fill="x",
            padx=17,
            pady=(4, 19)
        )

        stats = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        stats.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 12)
        )

        ctk.CTkLabel(
            stats,
            text="ВАШ АВТОМОБИЛЬ",
            text_color=BEIGE,
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=6,
            pady=(0, 12)
        )

        due = self.db.due(
            car["id"],
            car["mileage"]
        )

        overdue = sum(
            1 for item in due
            if item["overdue"]
        )

        metrics = ctk.CTkFrame(
            stats,
            fg_color="transparent"
        )

        metrics.pack(
            fill="both",
            expand=True
        )

        for label, value, color in [
            (
                "ТЕКУЩИЙ ПРОБЕГ",
                f"{car['mileage']:,} км".replace(",", " "),
                TEXT
            ),
            (
                "ГОД ВЫПУСКА",
                str(car["year"] or "Не указан"),
                TEXT
            ),
            (
                "ТРЕБУЮТ ВНИМАНИЯ",
                str(overdue),
                RED if overdue else GREEN
            )
        ]:

            tile = self.card(metrics)

            tile.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            ctk.CTkLabel(
                tile,
                text=label,
                text_color=MUTED,
                font=ctk.CTkFont(
                    size=9,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=12,
                pady=(18, 7)
            )

            ctk.CTkLabel(
                tile,
                text=value,
                text_color=color,
                font=ctk.CTkFont(
                    size=17,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=12,
                pady=(0, 18)
            )

        photo_box = ctk.CTkFrame(
            content,
            width=390,
            height=219,
            fg_color="#000000",
            corner_radius=12
        )

        photo_box.pack(
            side="right",
            padx=(8, 0)
        )

        photo_box.pack_propagate(False)

        photo_path = self.car_image_path(car)

        if photo_path.exists():

            try:
                with Image.open(photo_path) as source_image:
                    car_photo = source_image.convert("RGB")

                self.car_photo_image = ctk.CTkImage(
                    light_image=car_photo,
                    dark_image=car_photo,
                    size=(380, 214)
                )

                ctk.CTkLabel(
                    photo_box,
                    text="",
                    image=self.car_photo_image,
                    fg_color="transparent"
                ).pack(expand=True)

            except Exception as error:
                print("Ошибка загрузки фото автомобиля:", error)
                self._photo_placeholder(photo_box)

        else:
            self._photo_placeholder(photo_box)

        lower = ctk.CTkFrame(
            self.area,
            fg_color="transparent"
        )

        lower.pack(
            fill="both",
            expand=True
        )

        left = self.card(lower)

        left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 9)
        )

        right = self.card(
            lower,
            width=245
        )

        right.pack(
            side="left",
            fill="y",
            padx=(9, 0)
        )

        ctk.CTkLabel(
            left,
            text="Ближайшие напоминания",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=18,
            pady=(17, 10)
        )

        if due:

            for item in due[:5]:
                self.reminder_row(left, item)

        else:

            empty_state = ctk.CTkFrame(
                left,
                fg_color="transparent"
            )

            empty_state.pack(
                expand=True,
                fill="both",
                pady=20
            )

            ctk.CTkLabel(
                empty_state,
                text="◷",
                text_color=BEIGE,
                font=ctk.CTkFont(size=48)
            ).pack(pady=(25, 8))

            ctk.CTkLabel(
                empty_state,
                text="Пока всё спокойно",
                text_color=TEXT,
                font=ctk.CTkFont(
                    size=19,
                    weight="bold"
                )
            ).pack(pady=5)

            ctk.CTkLabel(
                empty_state,
                text="Добавьте обслуживание, и Lapka Motors напомнит,\nкогда придёт время повторить процедуру.",
                text_color=MUTED,
                font=ctk.CTkFont(size=12),
                justify="center"
            ).pack(pady=5)

            self.primary(
                empty_state,
                "＋ Добавить обслуживание",
                self.add_record,
                220
            ).pack(pady=15)

        ctk.CTkLabel(
            right,
            text="Быстрые действия",
            text_color=TEXT,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=16,
            pady=(18, 14)
        )

        self.primary(
            right,
            "＋ Добавить запись",
            self.add_record,
            210
        ).pack(
            padx=13,
            pady=5
        )

        self.secondary(
            right,
            "Мой гараж",
            lambda: self.show("Мой гараж"),
            210
        ).pack(
            padx=13,
            pady=5
        )

        self.secondary(
            right,
            "История обслуживания",
            lambda: self.show("Обслуживание"),
            210
        ).pack(
            padx=13,
            pady=5
        )

    def _photo_placeholder(self, parent):

        ctk.CTkLabel(
            parent,
            text="ФОТОГРАФИЯ АВТОМОБИЛЯ\nСКОРО ПОЯВИТСЯ",
            text_color="#8F877F",
            font=ctk.CTkFont(
                "Segoe UI",
                10,
                "bold"
            ),
            justify="center"
        ).pack(expand=True)

    def reminder_row(self, parent, item):

        row = ctk.CTkFrame(
            parent,
            fg_color=CARD2,
            corner_radius=11
        )

        row.pack(
            fill="x",
            padx=13,
            pady=5
        )

        ctk.CTkLabel(
            row,
            text="●",
            text_color=RED if item["overdue"] else BEIGE
        ).pack(
            side="left",
            padx=12
        )

        box = ctk.CTkFrame(
            row,
            fg_color="transparent"
        )

        box.pack(
            side="left",
            fill="x",
            expand=True,
            pady=8
        )

        ctk.CTkLabel(
            box,
            text=item["service"],
            text_color=TEXT,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(anchor="w")

        ctk.CTkLabel(
            box,
            text=item["status"],
            text_color=MUTED,
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w")

    def select_car(self, label):

        try:
            self.selected_id = int(
                label.split("|", 1)[0].strip()
            )

        except (ValueError, IndexError):
            return

        self.show(self.current_page)

    # =====================================================
    # ПОИСК ФОТОГРАФИЙ АВТОМОБИЛЕЙ
    # =====================================================

    def car_image_path(self, car):

        images_dir = (
            Path(__file__).resolve().parent
            / "assets"
            / "images"
        )

        fallback = images_dir / "__image_not_found__.png"

        if not images_dir.exists():
            return fallback

        brand = str(car.get("brand", "")).strip().lower()
        model = str(car.get("model", "")).strip().lower()

        image_names = {
            ("bmw", "1 series"): "bmw_1.png",
            ("bmw", "3 series"): "bmw_3.png",
            ("bmw", "5 series"): "bmw_5.png",
            ("bmw", "x3"): "bmw_x3.png",
            ("bmw", "x5"): "bmw_x5.png",

            ("lada", "granta"): "Lada_granta.png",
            ("lada", "kalina"): "Lada_kalina.png",
            ("lada", "niva"): "Lada_niva.png",
            ("lada", "vesta"): "Lada_vesta.png",

            ("opel", "astra"): "opel_astra.png",
            ("opel", "corsa"): "opel_corsa.png",
            ("opel", "insignia"): "opel_instiga.png",
            ("opel", "vectra"): "opel_vectra.png",
            ("opel", "zafira"): "opel_zafira.png",

            ("toyota", "camry"): "toyota_camry.png",
            ("toyota", "corolla"): "toyota_corolla.png",
            ("toyota", "land cruiser"): "toyota_landcruiser.png",
            ("toyota", "rav4"): "toyota_rav4.png",
            ("toyota", "yaris"): "toyota_yaris.png"
        }

        filename = image_names.get((brand, model))

        if filename:

            image_path = images_dir / filename

            if image_path.exists():
                return image_path

        def normalize(value):
            return re.sub(
                r"[^a-zа-я0-9]",
                "",
                value.lower()
            )

        brand_normalized = normalize(brand)
        model_normalized = normalize(model)

        try:

            for image_file in images_dir.iterdir():

                if image_file.suffix.lower() not in (
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".webp"
                ):
                    continue

                filename_normalized = normalize(
                    image_file.stem
                )

                if (
                    brand_normalized in filename_normalized
                    and model_normalized in filename_normalized
                ):
                    return image_file

        except OSError:
            pass

        return fallback

    # =====================================================
    # ГАРАЖ
    # =====================================================

    def garage(self):

        self.heading(
            "Мой гараж",
            "Ваша коллекция автомобилей"
        )

        cars = self.db.cars()

        top = ctk.CTkFrame(
            self.area,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            top,
            text=f"АВТОМОБИЛИ  /  {len(cars)}",
            text_color=MUTED,
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            )
        ).pack(side="left")

        add_button = self.primary(
            top,
            "＋ Добавить автомобиль",
            self.add_car,
            210
        )

        add_button.pack(side="right")

        if len(cars) >= MAX_CARS:

            add_button.configure(
                state="disabled",
                fg_color="#655D54",
                text="Достигнут лимит"
            )

        if not cars:

            self.empty(
                "Гараж пока пуст",
                "Добавьте первый автомобиль в Lapka Motors.",
                self.add_car
            )

            return

        container = ctk.CTkFrame(
            self.area,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True
        )

        self.garage_images = []

        for car in cars:

            is_selected = car["id"] == self.selected_id

            car_card = ctk.CTkFrame(
                container,
                fg_color="#111111" if is_selected else CARD,
                corner_radius=17,
                border_width=1,
                border_color=BEIGE if is_selected else "#35302B"
            )

            car_card.pack(
                fill="x",
                pady=7
            )

            content = ctk.CTkFrame(
                car_card,
                fg_color="transparent"
            )

            content.pack(
                fill="x",
                padx=16,
                pady=14
            )

            photo_box = ctk.CTkFrame(
                content,
                width=300,
                height=170,
                fg_color="#080808",
                corner_radius=12
            )

            photo_box.pack(
                side="left",
                padx=(0, 20)
            )

            photo_box.pack_propagate(False)

            photo_path = self.car_image_path(car)

            if photo_path.exists():

                try:

                    with Image.open(photo_path) as source:

                        photo = ImageOps.fit(
                            source.convert("RGB"),
                            (580, 320),
                            method=Image.Resampling.LANCZOS,
                            centering=(0.5, 0.52)
                        )

                        photo = ImageEnhance.Sharpness(
                            photo
                        ).enhance(1.18)

                        photo = ImageEnhance.Contrast(
                            photo
                        ).enhance(1.04)

                        canvas = photo.resize(
                            (290, 160),
                            Image.Resampling.LANCZOS
                        )

                    image = ctk.CTkImage(
                        light_image=canvas,
                        dark_image=canvas,
                        size=(290, 160)
                    )

                    self.garage_images.append(image)

                    ctk.CTkLabel(
                        photo_box,
                        text="",
                        image=image,
                        fg_color="transparent"
                    ).pack(expand=True)

                except Exception as error:

                    print(
                        "Ошибка загрузки фотографии:",
                        error
                    )

                    self._photo_placeholder(photo_box)

            else:

                ctk.CTkLabel(
                    photo_box,
                    text="LAPKA MOTORS",
                    text_color="#655D54",
                    font=ctk.CTkFont(
                        size=13,
                        weight="bold"
                    )
                ).pack(expand=True)

            info = ctk.CTkFrame(
                content,
                fg_color="transparent"
            )

            info.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 12)
            )

            if is_selected:

                ctk.CTkLabel(
                    info,
                    text="● ВЫБРАННЫЙ АВТОМОБИЛЬ",
                    text_color=BEIGE,
                    font=ctk.CTkFont(
                        size=9,
                        weight="bold"
                    )
                ).pack(
                    anchor="w",
                    pady=(2, 7)
                )

            ctk.CTkLabel(
                info,
                text=f"{car['brand']} {car['model']}",
                text_color=TEXT,
                font=ctk.CTkFont(
                    size=22,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                pady=(0, 16)
            )

            metrics = ctk.CTkFrame(
                info,
                fg_color="transparent"
            )

            metrics.pack(anchor="w")

            for title, value in [
                (
                    "ПРОБЕГ",
                    f"{car['mileage']:,} км".replace(",", " ")
                ),
                (
                    "ГОД",
                    str(car["year"] or "—")
                )
            ]:

                block = ctk.CTkFrame(
                    metrics,
                    fg_color="#242424",
                    corner_radius=9
                )

                block.pack(
                    side="left",
                    padx=(0, 9)
                )

                ctk.CTkLabel(
                    block,
                    text=title,
                    text_color=MUTED,
                    font=ctk.CTkFont(
                        size=9,
                        weight="bold"
                    )
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(9, 2)
                )

                ctk.CTkLabel(
                    block,
                    text=value,
                    text_color=TEXT,
                    font=ctk.CTkFont(
                        size=13,
                        weight="bold"
                    )
                ).pack(
                    anchor="w",
                    padx=12,
                    pady=(0, 9)
                )

            actions = ctk.CTkFrame(
                content,
                fg_color="transparent"
            )

            actions.pack(
                side="right",
                padx=(8, 0)
            )

            actions.grid_columnconfigure(
                (0, 1),
                weight=1
            )

            self.primary(
                actions,
                "Выбрано" if is_selected else "Выбрать",
                lambda cid=car["id"]: self.choose_car(cid),
                112
            ).grid(
                row=0,
                column=0,
                padx=4,
                pady=4,
                sticky="ew"
            )

            self.secondary(
                actions,
                "Профиль",
                lambda cid=car["id"]: self.car_profile(cid),
                112
            ).grid(
                row=0,
                column=1,
                padx=4,
                pady=4,
                sticky="ew"
            )

            self.secondary(
                actions,
                "Пробег",
                lambda cid=car["id"]: self.change_mileage(cid),
                112
            ).grid(
                row=1,
                column=0,
                padx=4,
                pady=4,
                sticky="ew"
            )

            self.secondary(
                actions,
                "Изменить",
                lambda cid=car["id"]: self.edit_car(cid),
                112
            ).grid(
                row=1,
                column=1,
                padx=4,
                pady=4,
                sticky="ew"
            )

            self.secondary(
                actions,
                "Удалить",
                lambda cid=car["id"]: self.remove_car(cid),
                112
            ).grid(
                row=2,
                column=0,
                columnspan=2,
                padx=4,
                pady=4,
                sticky="ew"
            )

    def choose_car(self, car_id):

        self.selected_id = car_id
        self.show("Главная")

    # =====================================================
    # ДОБАВЛЕНИЕ АВТОМОБИЛЯ
    # =====================================================

    def add_car(self):

        cars = self.db.cars()

        if len(cars) >= MAX_CARS:

            messagebox.showinfo(
                "Лимит автомобилей",
                f"В гараже можно сохранить не более {MAX_CARS} автомобилей."
            )

            return

        win = ctk.CTkToplevel(self)

        win.title("Добавить автомобиль")
        win.geometry("410x490")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Добавить автомобиль",
            text_color=BEIGE,
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        ).pack(pady=(24, 18))

        brand = ctk.StringVar(value="Opel")
        model = ctk.StringVar(value=BRANDS["Opel"][0])
        year = ctk.StringVar()
        mileage = ctk.StringVar(value="0")

        def label(text):

            ctk.CTkLabel(
                win,
                text=text,
                text_color=MUTED
            ).pack(
                anchor="w",
                padx=32
            )

        label("Марка")

        def change_brand(value):

            model_menu.configure(
                values=BRANDS[value]
            )

            model.set(
                BRANDS[value][0]
            )

        ctk.CTkOptionMenu(
            win,
            values=list(BRANDS),
            variable=brand,
            command=change_brand
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 12)
        )

        label("Модель")

        model_menu = ctk.CTkOptionMenu(
            win,
            values=BRANDS["Opel"],
            variable=model
        )

        model_menu.pack(
            fill="x",
            padx=32,
            pady=(4, 12)
        )

        label("Год выпуска (необязательно)")

        ctk.CTkEntry(
            win,
            textvariable=year,
            placeholder_text="Например, 2019"
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 12)
        )

        label("Текущий пробег, км")

        ctk.CTkEntry(
            win,
            textvariable=mileage
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 18)
        )

        def save():

            try:

                km = int(mileage.get().strip())

                y = (
                    int(year.get().strip())
                    if year.get().strip()
                    else None
                )

                if km < 0:
                    raise ValueError

                if y is not None and not (
                    1950 <= y <= date.today().year + 1
                ):
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Ошибка",
                    "Проверьте год и пробег.",
                    parent=win
                )

                return

            try:

                self.db.add_car(
                    brand.get(),
                    model.get(),
                    y,
                    km
                )

            except Exception as error:

                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось добавить автомобиль:\n{error}",
                    parent=win
                )

                return

            win.destroy()

            updated_cars = self.db.cars()

            if updated_cars:
                self.selected_id = updated_cars[-1]["id"]

            self.show("Мой гараж")

        self.primary(
            win,
            "Сохранить автомобиль",
            save,
            270
        ).pack()

    # =====================================================
    # РЕДАКТИРОВАНИЕ АВТОМОБИЛЯ
    # =====================================================

    def edit_car(self, car_id):

        car = next(
            (
                item for item in self.db.cars()
                if item["id"] == car_id
            ),
            None
        )

        if car is None:

            messagebox.showerror(
                "Ошибка",
                "Автомобиль не найден."
            )

            return

        win = ctk.CTkToplevel(self)

        win.title("Редактировать автомобиль")
        win.geometry("410x500")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Редактировать автомобиль",
            text_color=BEIGE,
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            )
        ).pack(pady=(22, 18))

        brand = ctk.StringVar(value=car["brand"])
        model = ctk.StringVar(value=car["model"])
        year = ctk.StringVar(value=str(car["year"] or ""))
        mileage = ctk.StringVar(value=str(car["mileage"]))

        def label(text):

            ctk.CTkLabel(
                win,
                text=text,
                text_color=MUTED
            ).pack(
                anchor="w",
                padx=32
            )

        label("Марка")

        def change_brand(value):

            model_menu.configure(
                values=BRANDS[value]
            )

            model.set(
                BRANDS[value][0]
            )

        ctk.CTkOptionMenu(
            win,
            values=list(BRANDS),
            variable=brand,
            command=change_brand
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 11)
        )

        label("Модель")

        model_menu = ctk.CTkOptionMenu(
            win,
            values=BRANDS.get(
                car["brand"],
                BRANDS["Opel"]
            ),
            variable=model
        )

        model_menu.pack(
            fill="x",
            padx=32,
            pady=(4, 11)
        )

        label("Год выпуска")

        ctk.CTkEntry(
            win,
            textvariable=year,
            placeholder_text="Например, 2019"
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 11)
        )

        label("Текущий пробег, км")

        ctk.CTkEntry(
            win,
            textvariable=mileage
        ).pack(
            fill="x",
            padx=32,
            pady=(4, 18)
        )

        def save():

            try:

                km = int(mileage.get().strip())

                y = (
                    int(year.get().strip())
                    if year.get().strip()
                    else None
                )

                if km < 0:
                    raise ValueError

                if y is not None and not (
                    1950 <= y <= date.today().year + 1
                ):
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Ошибка",
                    "Проверьте год и пробег.",
                    parent=win
                )

                return

            try:

                self.db.update_car(
                    car_id,
                    brand.get(),
                    model.get(),
                    y,
                    km
                )

            except Exception as error:

                messagebox.showerror(
                    "Ошибка",
                    str(error),
                    parent=win
                )

                return

            win.destroy()
            self.show("Мой гараж")

        self.primary(
            win,
            "Сохранить изменения",
            save,
            270
        ).pack()

    # =====================================================
    # УДАЛЕНИЕ АВТОМОБИЛЯ
    # =====================================================

    def remove_car(self, car_id):

        car = next(
            (
                item for item in self.db.cars()
                if item["id"] == car_id
            ),
            None
        )

        if car is None:
            return

        answer = messagebox.askyesno(
            "Удалить автомобиль",
            f"Удалить {car['brand']} {car['model']} и все связанные записи обслуживания?"
        )

        if not answer:
            return

        try:

            self.db.delete_car(car_id)

        except Exception as error:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось удалить автомобиль:\n{error}"
            )

            return

        remaining = self.db.cars()

        self.selected_id = (
            remaining[0]["id"]
            if remaining
            else None
        )

        self.show("Мой гараж")

    # =====================================================
    # ИЗМЕНЕНИЕ ПРОБЕГА
    # =====================================================

    def change_mileage(self, car_id):

        car = next(
            (
                item for item in self.db.cars()
                if item["id"] == car_id
            ),
            None
        )

        if car is None:

            messagebox.showerror(
                "Ошибка",
                "Автомобиль не найден."
            )

            return

        value = ctk.CTkInputDialog(
            title="Изменение пробега",
            text=f"Новый пробег {car['brand']} {car['model']} (км):"
        ).get_input()

        if value is None:
            return

        try:

            km = int(value.strip())

            if km < 0:
                raise ValueError

            if km < car["mileage"]:

                answer = messagebox.askyesno(
                    "Проверка пробега",
                    "Новый пробег меньше предыдущего. Вы действительно хотите сохранить его?"
                )

                if not answer:
                    return

            self.db.set_mileage(
                car_id,
                km
            )

        except (ValueError, AssertionError) as error:

            messagebox.showerror(
                "Ошибка",
                str(error) or "Введите корректный пробег."
            )

            return

        except Exception as error:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось обновить пробег:\n{error}"
            )

            return

        self.show(self.current_page)

    # =====================================================
    # БОЛЯЧКИ АВТОМОБИЛЯ
    # =====================================================

    def ailments(self):

        self.heading(
            "Болячки автомобиля",
            "Узнайте о типичных неисправностях вашей модели"
        )

        cars = self.db.cars()

        if not cars:
            self.empty(
                "Нет автомобиля",
                "Сначала добавьте автомобиль в гараж.",
                self.add_car
            )
            return

        car = next(
            (
                item for item in cars
                if item["id"] == self.selected_id
            ),
            cars[0]
        )

        self.selected_id = car["id"]

        panel = self.card()
        panel.pack(fill="x", pady=10)

        ctk.CTkLabel(
            panel,
            text=f"{car['brand']} {car['model']}",
            text_color=BEIGE,
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack(anchor="w", padx=22, pady=(22, 8))

        ctk.CTkLabel(
            panel,
            text=(
                "Здесь вы сможете изучить распространённые "
                "проблемы вашего автомобиля, узнать о слабых "
                "местах модели и почитать отзывы владельцев."
            ),
            text_color=MUTED,
            wraplength=700,
            justify="left"
        ).pack(anchor="w", padx=22, pady=(0, 20))

        query = quote(
            f"{car['brand']} {car['model']} болячки неисправности"
        )

        self.primary(
            panel,
            "Изучить болячки на Drom",
            lambda: webbrowser.open(
                f"https://www.google.com/search?q={query}+site%3Adrom.ru"
            ),
            250
        ).pack(anchor="w", padx=22, pady=(0, 12))

        self.secondary(
            panel,
            "Поиск в интернете",
            lambda: webbrowser.open(
                f"https://yandex.ru/search/?text={query}"
            ),
            250
        ).pack(anchor="w", padx=22, pady=(0, 22))

    # =====================================================
    # АВТОСЕРВИС
    # =====================================================

    def auto_service(self):

        self.heading(
            "Автосервис",
            "Найдите подходящий сервис для вашего автомобиля"
        )

        cars = self.db.cars()

        if not cars:

            self.empty(
                "Нет автомобилей",
                "Добавьте машину в гараж, чтобы продолжить.",
                self.add_car
            )

            return

        car = next(
            (
                item for item in cars
                if item["id"] == self.selected_id
            ),
            cars[0]
        )

        self.selected_id = car["id"]

        ctk.CTkLabel(
            self.area,
            text=f"Автомобиль: {car['brand']} {car['model']}",
            text_color=BEIGE,
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w", pady=(0, 18))

        categories = [
            (
                "Автосервисы",
                "Ремонт и обслуживание",
                "🔧"
            ),
            (
                "Шиномонтаж",
                "Замена и ремонт шин",
                "◉"
            ),
            (
                "Автомойки",
                "Мойка и уход за кузовом",
                "🚘"
            ),
            (
                "Диагностика",
                "Компьютерная диагностика",
                "⚙"
            )
        ]

        for category, description, icon in categories:

            panel = self.card()

            panel.pack(
                fill="x",
                pady=7
            )

            content = ctk.CTkFrame(
                panel,
                fg_color="transparent"
            )

            content.pack(
                fill="x",
                padx=20,
                pady=15
            )

            ctk.CTkLabel(
                content,
                text=icon,
                text_color=BEIGE,
                font=ctk.CTkFont(size=27)
            ).pack(side="left", padx=(0, 15))

            info = ctk.CTkFrame(
                content,
                fg_color="transparent"
            )

            info.pack(
                side="left",
                fill="x",
                expand=True
            )

            ctk.CTkLabel(
                info,
                text=category,
                text_color=TEXT,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=description,
                text_color=MUTED,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", pady=(3, 0))

            self.primary(
                content,
                "Найти на карте",
                lambda cat=category: self.open_service_map(cat),
                170
            ).pack(side="right")

    def open_service_map(self, category):

        query = quote(category)

        url = (
            "https://yandex.ru/maps/?text="
            + query
        )

        webbrowser.open(url)

    # =====================================================
    # ПРОФИЛЬ АВТОМОБИЛЯ
    # =====================================================

    def car_profile(self, car_id):

        cars = self.db.cars()

        car = next(
            (
                item for item in cars
                if item["id"] == car_id
            ),
            None
        )

        if car is None:

            messagebox.showerror(
                "Ошибка",
                "Автомобиль не найден."
            )

            return

        self.clear()

        self.current_page = "Мой гараж"

        for name, button in self.nav.items():

            active = name == "Мой гараж"

            button.configure(
                fg_color=BEIGE if active else "transparent",
                text_color="#211A14" if active else TEXT,
                text=self._navigation_text(name)
            )

        self.heading(
            "Профиль автомобиля",
            "Подробная информация о вашем автомобиле"
        )

        self.secondary(
            self.area,
            "← Назад в гараж",
            lambda: self.show("Мой гараж"),
            170
        ).pack(anchor="w", pady=(0, 18))

        panel = self.card()

        panel.pack(
            fill="x",
            pady=5
        )

        ctk.CTkLabel(
            panel,
            text=f"{car['brand']} {car['model']}",
            text_color=BEIGE,
            font=ctk.CTkFont(size=25, weight="bold")
        ).pack(anchor="w", padx=22, pady=(20, 14))

        photo_path = self.car_image_path(car)

        if photo_path.exists():

            try:

                with Image.open(photo_path) as source:
                    photo = source.convert("RGB")

                self.profile_photo = ctk.CTkImage(
                    light_image=photo,
                    dark_image=photo,
                    size=(450, 230)
                )

                ctk.CTkLabel(
                    panel,
                    text="",
                    image=self.profile_photo
                ).pack(padx=20, pady=(0, 15))

            except Exception as error:

                print("Ошибка фотографии:", error)

                self._photo_placeholder(panel)

        else:

            self._photo_placeholder(panel)

        details = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        details.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        values = [
            ("Марка", car["brand"]),
            ("Модель", car["model"]),
            ("Год выпуска", car["year"] or "Не указан"),
            (
                "Текущий пробег",
                f"{car['mileage']:,} км".replace(",", " ")
            )
        ]

        for index, (name, value) in enumerate(values):

            tile = self.card(details)

            tile.grid(
                row=index // 2,
                column=index % 2,
                padx=5,
                pady=5,
                sticky="nsew"
            )

            ctk.CTkLabel(
                tile,
                text=name.upper(),
                text_color=MUTED,
                font=ctk.CTkFont(size=9, weight="bold")
            ).pack(anchor="w", padx=13, pady=(12, 4))

            ctk.CTkLabel(
                tile,
                text=str(value),
                text_color=TEXT,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="w", padx=13, pady=(0, 12))

        details.grid_columnconfigure((0, 1), weight=1)

        actions = ctk.CTkFrame(
            panel,
            fg_color="transparent"
        )

        actions.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.primary(
            actions,
            "Изменить автомобиль",
            lambda: self.edit_car(car_id),
            190
        ).pack(side="left", padx=(0, 8))

        self.secondary(
            actions,
            "Изменить пробег",
            lambda: self.change_mileage(car_id),
            160
        ).pack(side="left", padx=8)

        # История обслуживания
        history_panel = self.card()

        history_panel.pack(
            fill="both",
            expand=True,
            pady=15
        )

        ctk.CTkLabel(
            history_panel,
            text="История обслуживания",
            text_color=TEXT,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(17, 10))

        records = self.db.records()

        car_records = [
            record for record in records
            if (
                record.get("car_id") == car_id
                or (
                    record.get("car_id") is None
                    and record.get("brand") == car["brand"]
                    and record.get("model") == car["model"]
                )
            )
        ]

        if not car_records:

            ctk.CTkLabel(
                history_panel,
                text="Записей обслуживания пока нет.",
                text_color=MUTED
            ).pack(pady=25)

        else:

            for record in reversed(car_records[-8:]):

                row = ctk.CTkFrame(
                    history_panel,
                    fg_color=CARD2,
                    corner_radius=10
                )

                row.pack(
                    fill="x",
                    padx=14,
                    pady=4
                )

                ctk.CTkLabel(
                    row,
                    text=record.get("service", "Обслуживание"),
                    text_color=TEXT,
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(anchor="w", padx=12, pady=(9, 2))

                ctk.CTkLabel(
                    row,
                    text=(
                        f"{record.get('date', '')}   •   "
                        f"{record.get('mileage', 0):,} км"
                    ).replace(",", " "),
                    text_color=MUTED,
                    font=ctk.CTkFont(size=10)
                ).pack(anchor="w", padx=12, pady=(0, 9))

    # =====================================================
    # ОБСЛУЖИВАНИЕ
    # =====================================================

    def service(self):

        self.heading(
            "Обслуживание",
            "История работ по всем автомобилям"
        )

        top = ctk.CTkFrame(
            self.area,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            pady=(0, 16)
        )

        self.primary(
            top,
            "＋ Добавить запись",
            self.add_record,
            190
        ).pack(side="right")

        records = self.db.records()
        cars = self.db.cars()

        if not records:

            self.empty(
                "История пока пуста",
                "Добавьте первую запись обслуживания.",
                self.add_record,
                "＋ Добавить запись"
            )

            return

        for record in reversed(records):

            panel = self.card()

            panel.pack(
                fill="x",
                pady=6
            )

            car_name = (
                f"{record.get('brand', '')} "
                f"{record.get('model', '')}"
            ).strip()

            if not car_name:

                car = next(
                    (
                        item for item in cars
                        if item["id"] == record.get("car_id")
                    ),
                    None
                )

                if car:
                    car_name = f"{car['brand']} {car['model']}"
                else:
                    car_name = "Автомобиль"

            top_line = ctk.CTkFrame(
                panel,
                fg_color="transparent"
            )

            top_line.pack(
                fill="x",
                padx=17,
                pady=(13, 4)
            )

            ctk.CTkLabel(
                top_line,
                text=record.get("service", "Обслуживание"),
                text_color=TEXT,
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left")

            ctk.CTkLabel(
                top_line,
                text=record.get("date", ""),
                text_color=BEIGE,
                font=ctk.CTkFont(size=11)
            ).pack(side="right")

            ctk.CTkLabel(
                panel,
                text=(
                    f"{car_name}  •  "
                    f"{record.get('mileage', 0):,} км"
                ).replace(",", " "),
                text_color=MUTED,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", padx=17, pady=3)

            note = record.get("note", "")

            if note:

                ctk.CTkLabel(
                    panel,
                    text=note,
                    text_color=MUTED,
                    wraplength=650,
                    justify="left"
                ).pack(anchor="w", padx=17, pady=(3, 7))

            self.secondary(
                panel,
                "Удалить запись",
                lambda rid=record["id"]: self.delete_record(rid),
                145
            ).pack(anchor="e", padx=15, pady=(5, 13))

    # =====================================================
    # ДОБАВЛЕНИЕ ЗАПИСИ ОБСЛУЖИВАНИЯ
    # =====================================================

    def add_record(self):

        cars = self.db.cars()

        if not cars:

            messagebox.showinfo(
                "Нет автомобилей",
                "Сначала добавьте машину в гараж."
            )

            return

        win = ctk.CTkToplevel(self)

        win.title("Новое обслуживание")
        win.geometry("470x690")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(
            win,
            text="Новая запись",
            text_color=BEIGE,
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack(pady=(20, 15))

        def field_label(text):

            ctk.CTkLabel(
                win,
                text=text,
                text_color=MUTED,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", padx=35)

        selected_car = ctk.StringVar(
            value=(
                f"{cars[0]['id']} | "
                f"{cars[0]['brand']} {cars[0]['model']}"
            )
        )

        field_label("Автомобиль")

        ctk.CTkOptionMenu(
            win,
            variable=selected_car,
            values=[
                f"{car['id']} | {car['brand']} {car['model']}"
                for car in cars
            ],
            width=390
        ).pack(padx=30, pady=(4, 12))

        service = ctk.StringVar(value=SERVICES[0])

        field_label("Процедура")

        ctk.CTkOptionMenu(
            win,
            variable=service,
            values=SERVICES,
            width=390
        ).pack(padx=30, pady=(4, 12))

        field_label("Дата (ДД.ММ.ГГГГ)")

        when = ctk.CTkEntry(
            win,
            width=390,
            placeholder_text="Например, 16.11.2026"
        )

        when.insert(0, date.today().strftime("%d.%m.%Y"))

        when.pack(padx=30, pady=(4, 12))

        field_label("Пробег при обслуживании, км")

        mileage = ctk.CTkEntry(
            win,
            width=390,
            placeholder_text="Например, 85000"
        )

        mileage.pack(padx=30, pady=(4, 12))

        field_label("Интервал в днях (0 — отключить)")

        days = ctk.CTkEntry(
            win,
            width=390
        )

        days.insert(0, "0")

        days.pack(padx=30, pady=(4, 12))

        field_label("Интервал в километрах (0 — отключить)")

        km_interval = ctk.CTkEntry(
            win,
            width=390
        )

        km_interval.insert(0, "0")

        km_interval.pack(padx=30, pady=(4, 12))

        field_label("Комментарий")

        note = ctk.CTkEntry(
            win,
            width=390,
            placeholder_text="Дополнительная информация"
        )

        note.pack(padx=30, pady=(4, 18))

        def save():

            try:

                parsed = datetime.strptime(
                    when.get().strip(),
                    "%d.%m.%Y"
                ).date()

                km = int(mileage.get().strip())
                dd = int(days.get().strip())
                kk = int(km_interval.get().strip())

                if km < 0 or dd < 0 or kk < 0:
                    raise ValueError

                if parsed > date.today():
                    raise ValueError

            except ValueError:

                messagebox.showerror(
                    "Ошибка",
                    "Проверьте дату и числовые значения.",
                    parent=win
                )

                return

            try:

                cid = int(
                    selected_car.get().split("|", 1)[0].strip()
                )

                self.db.add_record(
                    cid,
                    service.get(),
                    parsed.isoformat(),
                    km,
                    dd or None,
                    kk or None,
                    note.get().strip()
                )

            except Exception as error:

                messagebox.showerror(
                    "Ошибка",
                    f"Не удалось добавить запись:\n{error}",
                    parent=win
                )

                return

            win.destroy()

            self.show("Обслуживание")

        self.primary(
            win,
            "Сохранить запись",
            save,
            270
        ).pack(pady=(0, 15))

    # =====================================================
    # УДАЛЕНИЕ ЗАПИСИ
    # =====================================================

    def delete_record(self, rid):

        if not messagebox.askyesno(
            "Удаление",
            "Удалить запись обслуживания?"
        ):
            return

        try:

            self.db.delete_record(rid)
            self.show("Обслуживание")

        except Exception as error:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось удалить запись:\n{error}"
            )

    # =====================================================
    # НАПОМИНАНИЯ
    # =====================================================

    def reminders(self):

        self.heading(
            "Напоминания",
            "Сроки обслуживания по датам и пробегу"
        )

        cars = self.db.cars()

        if not cars:

            self.empty(
                "Нет автомобилей",
                "Сначала добавьте машину в гараж.",
                self.add_car
            )

            return

        all_due = []

        for car in cars:

            try:

                due_items = self.db.due(
                    car["id"],
                    car["mileage"]
                )

                for item in due_items:

                    all_due.append({
                        "car": car,
                        "item": item
                    })

            except Exception as error:

                print(
                    f"Ошибка получения напоминаний: {error}"
                )

        if not all_due:

            panel = self.card()

            panel.pack(
                fill="x",
                pady=15
            )

            ctk.CTkLabel(
                panel,
                text="Пока всё спокойно",
                text_color=GREEN,
                font=ctk.CTkFont(size=22, weight="bold")
            ).pack(pady=(25, 8))

            ctk.CTkLabel(
                panel,
                text="Нет процедур с заданными интервалами.",
                text_color=MUTED
            ).pack(pady=(0, 25))

            return

        for entry in all_due:

            car = entry["car"]
            item = entry["item"]

            panel = self.card()

            panel.pack(
                fill="x",
                pady=6
            )

            row = ctk.CTkFrame(
                panel,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=17,
                pady=14
            )

            color = RED if item["overdue"] else BEIGE

            ctk.CTkLabel(
                row,
                text="●",
                text_color=color,
                font=ctk.CTkFont(size=18)
            ).pack(side="left", padx=(0, 12))

            info = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )

            info.pack(
                side="left",
                fill="x",
                expand=True
            )

            ctk.CTkLabel(
                info,
                text=item["service"],
                text_color=TEXT,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w")

            ctk.CTkLabel(
                info,
                text=(
                    f"{car['brand']} {car['model']}  •  "
                    f"{item['status']}"
                ),
                text_color=MUTED,
                font=ctk.CTkFont(size=11)
            ).pack(anchor="w", pady=(4, 0))

            if item["overdue"]:

                ctk.CTkLabel(
                    row,
                    text="Просрочено",
                    text_color=RED,
                    font=ctk.CTkFont(size=10, weight="bold")
                ).pack(side="right")

    # =====================================================
    # НАСТРОЙКИ
    # =====================================================

    def settings(self):

        self.heading(
            "Настройки",
            "Параметры приложения Lapka Motors"
        )

        # Оформление
        appearance = self.card()

        appearance.pack(
            fill="x",
            pady=7
        )

        ctk.CTkLabel(
            appearance,
            text="Оформление",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 5))

        ctk.CTkLabel(
            appearance,
            text="Тёмная тема, графитовые карточки и бежевые акценты.",
            text_color=MUTED
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # Язык
        language_panel = self.card()

        language_panel.pack(
            fill="x",
            pady=7
        )

        ctk.CTkLabel(
            language_panel,
            text="Язык приложения",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 5))

        ctk.CTkLabel(
            language_panel,
            text="Выберите язык интерфейса",
            text_color=MUTED
        ).pack(anchor="w", padx=20, pady=(0, 12))

        language_var = ctk.StringVar(
            value="English" if CURRENT_LANGUAGE == "en" else "Русский"
        )

        ctk.CTkOptionMenu(
            language_panel,
            variable=language_var,
            values=["Русский", "English"],
            command=self.set_language,
            width=220
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        # Хранение данных
        storage = self.card()

        storage.pack(
            fill="x",
            pady=7
        )

        ctk.CTkLabel(
            storage,
            text="Хранение данных",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 5))

        ctk.CTkLabel(
            storage,
            text="Данные автомобилей и обслуживания хранятся в подключённой базе данных.",
            text_color=MUTED,
            wraplength=650,
            justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 18))

        # Информация
        about = self.card()

        about.pack(
            fill="x",
            pady=7
        )

        ctk.CTkLabel(
            about,
            text="О приложении",
            text_color=TEXT,
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(anchor="w", padx=20, pady=(18, 5))

        ctk.CTkLabel(
            about,
            text="Lapka Motors — личный помощник автомобилиста.",
            text_color=MUTED
        ).pack(anchor="w", padx=20, pady=(0, 18))

    def set_language(self, selected_language):

        global CURRENT_LANGUAGE

        CURRENT_LANGUAGE = (
            "en" if selected_language == "English" else "ru"
        )

        try:

            LANGUAGE_FILE.write_text(
                CURRENT_LANGUAGE,
                encoding="utf-8"
            )

        except OSError as error:

            messagebox.showerror(
                "Ошибка",
                f"Не удалось сохранить язык:\n{error}"
            )

            return

        self.show(self.current_page)


# =========================================================
# ЗАПУСК ПРИЛОЖЕНИЯ И АВТОРИЗАЦИЯ
# =========================================================

print("ПРОВЕРКА: дошли до запуска main.py")

if __name__ == "__main__":

    print("Проверяем авторизацию...")

    user = get_current_user()

    print("Текущий пользователь:", user)

    if user is None:

        print("Пользователь не авторизован. Открываем окно входа.")

        auth_window = AuthWindow()
        auth_window.mainloop()

        if auth_window.authenticated:

            print("Авторизация успешна. Запускаем Lapka Motors.")

            app = LapkaApp()
            app.mainloop()

        else:

            print("Пользователь не прошёл авторизацию.")

    else:

        print("Пользователь уже авторизован.")

        app = LapkaApp()
        app.mainloop()