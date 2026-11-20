
from datetime import date, datetime, timedelta

from auth import supabase, get_user_id


class CloudDatabase:
    def __init__(self):
        self.user_id = get_user_id()

        if not self.user_id:
            raise RuntimeError(
                "Для работы с облачной базой необходимо войти в аккаунт."
            )

    # Преобразование даты в формат для Supabase
    @staticmethod
    def _to_iso_date(value):
        if isinstance(value, datetime):
            return value.date().isoformat()

        if isinstance(value, date):
            return value.isoformat()

        value = str(value).strip()

        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return datetime.strptime(value, "%d.%m.%Y").date().isoformat()

    # Форматирование даты для интерфейса
    @staticmethod
    def _display_date(value):
        if not value:
            return ""

        return date.fromisoformat(str(value)[:10]).strftime("%d.%m.%Y")

    # Автомобили
    def cars(self):
        response = (
            supabase.table("cars")
            .select("*")
            .eq("user_id", self.user_id)
            .execute()
        )

        return response.data or []

    def add_car(self, brand, model, year, mileage):
        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")

        return supabase.table("cars").insert({
            "user_id": self.user_id,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage
        }).execute()

    def update_car(self, car_id, brand, model, year, mileage):
        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")

        return (
            supabase.table("cars")
            .update({
                "brand": brand,
                "model": model,
                "year": year,
                "mileage": mileage
            })
            .eq("id", car_id)
            .eq("user_id", self.user_id)
            .execute()
        )

    def set_mileage(self, car_id, mileage):
        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")

        current = (
            supabase.table("cars")
            .select("mileage")
            .eq("id", car_id)
            .eq("user_id", self.user_id)
            .execute()
        )

        if not current.data:
            raise ValueError("Автомобиль не найден")

        if mileage < current.data[0]["mileage"]:
            raise ValueError("Новый пробег меньше сохранённого")

        return (
            supabase.table("cars")
            .update({"mileage": mileage})
            .eq("id", car_id)
            .eq("user_id", self.user_id)
            .execute()
        )

    def delete_car(self, car_id):
        return (
            supabase.table("cars")
            .delete()
            .eq("id", car_id)
            .eq("user_id", self.user_id)
            .execute()
        )

    # Обслуживание
    def add_record(self, car_id, service, when, mileage, days, km, note):
        return supabase.table("records").insert({
            "user_id": self.user_id,
            "car_id": car_id,
            "service_type": service,
            "service_date": self._to_iso_date(when),
            "mileage": mileage,
            "interval_days": days,
            "interval_km": km,
            "note": note or ""
        }).execute()

    def records(self, car_id=None):
        query = (
            supabase.table("records")
            .select("*")
            .eq("user_id", self.user_id)
        )

        if car_id is not None:
            query = query.eq("car_id", car_id)

        response = query.order(
            "service_date", desc=True
        ).execute()

        cars = {
            str(car["id"]): car
            for car in self.cars()
        }

        result = []

        for record in response.data or []:
            car = cars.get(str(record["car_id"]))

            if not car:
                continue

            result.append({
                "id": record["id"],
                "car_id": record["car_id"],
                "service": record["service_type"],
                "date": self._display_date(record["service_date"]),
                "mileage": record["mileage"],
                "note": record.get("note") or "",
                "brand": car["brand"],
                "model": car["model"]
            })

        return result

    def due(self, car_id, mileage_now):
        today = date.today()

        response = (
            supabase.table("records")
            .select("*")
            .eq("user_id", self.user_id)
            .eq("car_id", car_id)
            .order("service_date", desc=True)
            .execute()
        )

        latest = {}

        for record in response.data or []:
            service = record["service_type"]

            if service not in latest:
                latest[service] = record

        items = []

        for record in latest.values():
            last = date.fromisoformat(record["service_date"])

            days = record.get("interval_days")
            km = record.get("interval_km")

            due_date = (
                last + timedelta(days=days)
                if days else None
            )

            due_km = (
                record["mileage"] + km
                if km else None
            )

            parts = []
            overdue = False

            if due_date:
                delta = (due_date - today).days

                parts.append(
                    "срок наступил"
                    if delta <= 0
                    else f"через {delta} дн."
                )

                overdue = overdue or delta <= 0

            if due_km is not None:
                remain = due_km - mileage_now

                parts.append(
                    "пробег достигнут"
                    if remain <= 0
                    else f"через {remain:,} км".replace(",", " ")
                )

                overdue = overdue or remain <= 0

            if parts:
                items.append({
                    "service": record["service_type"],
                    "status": "  •  ".join(parts),
                    "overdue": overdue
                })

        return items

    def delete_record(self, record_id):
        return (
            supabase.table("records")
            .delete()
            .eq("id", record_id)
            .eq("user_id", self.user_id)
            .execute()
        )

    # Расходы
    def add_expense(self, car_id, category, when, amount, mileage, note=""):
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")

        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")

        return supabase.table("expenses").insert({
            "user_id": self.user_id,
            "car_id": car_id,
            "category": category,
            "expense_date": self._to_iso_date(when),
            "amount": amount,
            "mileage": mileage,
            "note": note or ""
        }).execute()

    def expenses(self, car_id=None):
        query = (
            supabase.table("expenses")
            .select("*")
            .eq("user_id", self.user_id)
        )

        if car_id is not None:
            query = query.eq("car_id", car_id)

        response = query.order(
            "expense_date", desc=True
        ).execute()

        cars = {
            str(car["id"]): car
            for car in self.cars()
        }

        result = []

        for expense in response.data or []:
            car = cars.get(str(expense["car_id"]))

            if not car:
                continue

            result.append({
                "id": expense["id"],
                "car_id": expense["car_id"],
                "category": expense["category"],
                "date": self._display_date(expense["expense_date"]),
                "amount": expense["amount"],
                "mileage": expense["mileage"],
                "note": expense.get("note") or "",
                "brand": car["brand"],
                "model": car["model"]
            })

        return result

    def expense_total(self, car_id=None):
        query = (
            supabase.table("expenses")
            .select("amount")
            .eq("user_id", self.user_id)
        )

        if car_id is not None:
            query = query.eq("car_id", car_id)

        response = query.execute()

        return sum(
            float(item["amount"])
            for item in (response.data or [])
        )

    def delete_expense(self, expense_id):
        return (
            supabase.table("expenses")
            .delete()
            .eq("id", expense_id)
            .eq("user_id", self.user_id)
            .execute()
        )
