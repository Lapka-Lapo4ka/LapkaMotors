
import customtkinter as ctk
from tkinter import messagebox

from auth import (
    register_user,
    login_user,
    reset_password
)


class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.authenticated = False

        self.title("Lapka Auto — Авторизация")
        self.geometry("440x570")
        self.resizable(False, False)

        self.configure(fg_color="#111111")

        ctk.set_appearance_mode("dark")

        self.build_interface()

    def build_interface(self):
        self.container = ctk.CTkFrame(
            self,
            fg_color="#1B1B1B",
            corner_radius=20
        )
        self.container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        ctk.CTkLabel(
            self.container,
            text="LAPKA AUTO",
            font=("Arial", 30, "bold"),
            text_color="#D6C3A5"
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            self.container,
            text="Твой автомобиль. Под твоим контролем.",
            font=("Arial", 12),
            text_color="#999999"
        ).pack(pady=(0, 30))

        ctk.CTkLabel(
            self.container,
            text="Вход в аккаунт",
            font=("Arial", 21, "bold"),
            text_color="#FFFFFF"
        ).pack(pady=(0, 20))

        self.email_entry = ctk.CTkEntry(
            self.container,
            width=320,
            height=45,
            placeholder_text="Электронная почта",
            corner_radius=10
        )
        self.email_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(
            self.container,
            width=320,
            height=45,
            placeholder_text="Пароль",
            show="*",
            corner_radius=10
        )
        self.password_entry.pack(pady=8)

        ctk.CTkButton(
            self.container,
            text="ВОЙТИ",
            width=320,
            height=45,
            corner_radius=10,
            fg_color="#C8B28F",
            hover_color="#A9916D",
            text_color="#111111",
            font=("Arial", 14, "bold"),
            command=self.login
        ).pack(pady=(22, 10))

        ctk.CTkButton(
            self.container,
            text="Создать аккаунт",
            width=320,
            height=40,
            corner_radius=10,
            fg_color="#333333",
            hover_color="#444444",
            text_color="#FFFFFF",
            command=self.register
        ).pack(pady=5)

        ctk.CTkButton(
            self.container,
            text="Забыли пароль?",
            fg_color="transparent",
            hover_color="#292929",
            text_color="#C8B28F",
            command=self.reset_password
        ).pack(pady=8)

        ctk.CTkLabel(
            self.container,
            text="Ваши данные доступны на любом компьютере",
            font=("Arial", 10),
            text_color="#777777"
        ).pack(side="bottom", pady=20)

    def get_credentials(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showwarning(
                "Внимание",
                "Введите почту и пароль."
            )
            return None, None

        return email, password

    def login(self):
        email, password = self.get_credentials()

        if not email:
            return

        try:
            login_user(email, password)

            self.authenticated = True
            self.destroy()

        except Exception as error:
            messagebox.showerror(
                "Ошибка входа",
                str(error)
            )

    def register(self):
        email, password = self.get_credentials()

        if not email:
            return

        if len(password) < 6:
            messagebox.showwarning(
                "Пароль",
                "Пароль должен содержать не менее 6 символов."
            )
            return

        try:
            response = register_user(email, password)

            if getattr(response, "session", None):
                self.authenticated = True
                self.destroy()
            else:
                messagebox.showinfo(
                    "Регистрация",
                    "Аккаунт создан! Проверьте почту и подтвердите регистрацию. "
                    "После подтверждения войдите в приложение."
                )

        except Exception as error:
            messagebox.showerror(
                "Ошибка регистрации",
                str(error)
            )

    def reset_password(self):
        email = self.email_entry.get().strip()

        if not email:
            messagebox.showwarning(
                "Восстановление пароля",
                "Сначала введите электронную почту."
            )
            return

        try:
            reset_password(email)

            messagebox.showinfo(
                "Восстановление",
                "Если адрес зарегистрирован, на него придёт письмо "
                "для восстановления пароля."
            )

        except Exception as error:
            messagebox.showerror(
                "Ошибка",
                str(error)
            )
