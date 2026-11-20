
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, ClientOptions
from supabase_auth import SyncSupportedStorage

# Настройки
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Проверь настройки Supabase в файле .env")


# Файл хранения сессии
SESSION_PATH = Path(__file__).resolve().parent / "session.json"


# Собственное хранилище сессии
class FileSessionStorage(SyncSupportedStorage):

    def get_item(self, key: str):
        if not SESSION_PATH.exists():
            return None

        try:
            data = json.loads(
                SESSION_PATH.read_text(encoding="utf-8")
            )
            return data.get(key)

        except (OSError, json.JSONDecodeError):
            return None

    def set_item(self, key: str, value: str):
        data = {}

        if SESSION_PATH.exists():
            try:
                data = json.loads(
                    SESSION_PATH.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                data = {}

        data[key] = value

        SESSION_PATH.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8"
        )

    def remove_item(self, key: str):
        if not SESSION_PATH.exists():
            return

        try:
            data = json.loads(
                SESSION_PATH.read_text(encoding="utf-8")
            )

            data.pop(key, None)

            SESSION_PATH.write_text(
                json.dumps(data, ensure_ascii=False),
                encoding="utf-8"
            )

        except (OSError, json.JSONDecodeError):
            pass


# Подключение Supabase
options = ClientOptions(
    persist_session=True,
    auto_refresh_token=True,
    storage=FileSessionStorage()
)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=options
)


# РЕГИСТРАЦИЯ
def register_user(email, password):
    try:
        return supabase.auth.sign_up({
            "email": email,
            "password": password
        })
    except Exception as error:
        raise Exception(f"Ошибка регистрации: {error}")


# ВХОД
def login_user(email, password):
    try:
        return supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception as error:
        raise Exception(f"Ошибка входа: {error}")


# ТЕКУЩИЙ ПОЛЬЗОВАТЕЛЬ
def get_current_user():
    try:
        session = supabase.auth.get_session()

        if session is None:
            return None

        response = supabase.auth.get_user()
        return response.user

    except Exception:
        return None


# ID ПОЛЬЗОВАТЕЛЯ
def get_user_id():
    user = get_current_user()

    if user is None:
        return None

    return user.id


# ПРОВЕРКА ВХОДА
def is_logged_in():
    return get_current_user() is not None


# ВЫХОД
def logout_user():
    try:
        supabase.auth.sign_out()
        return True
    except Exception as error:
        raise Exception(f"Ошибка выхода: {error}")


# ВОССТАНОВЛЕНИЕ ПАРОЛЯ
def reset_password(email):
    try:
        supabase.auth.reset_password_for_email(email)
        return True
    except Exception as error:
        raise Exception(f"Ошибка восстановления пароля: {error}")
