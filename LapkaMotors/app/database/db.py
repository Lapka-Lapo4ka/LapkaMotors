
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "lapka_auto.db"

class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS cars(
                id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT NOT NULL,
                model TEXT NOT NULL, year INTEGER, mileage INTEGER NOT NULL DEFAULT 0)""")
            con.execute("""CREATE TABLE IF NOT EXISTS records(
                id INTEGER PRIMARY KEY AUTOINCREMENT, car_id INTEGER NOT NULL,
                service_type TEXT NOT NULL, service_date TEXT NOT NULL,
                mileage INTEGER NOT NULL DEFAULT 0, interval_days INTEGER,
                interval_km INTEGER, note TEXT DEFAULT '',
                FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE)""")

            con.execute("""CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                amount REAL NOT NULL,
                mileage INTEGER NOT NULL DEFAULT 0,
                note TEXT DEFAULT '',
                FOREIGN KEY(car_id) REFERENCES cars(id) ON DELETE CASCADE
            )""")

    def connect(self):
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def cars(self):
        with self.connect() as con:
            return [dict(x) for x in con.execute("SELECT * FROM cars ORDER BY id DESC")]

    def add_car(self, brand, model, year, mileage):
        with self.connect() as con:
            con.execute("INSERT INTO cars(brand,model,year,mileage) VALUES(?,?,?,?)",
                        (brand, model, year, mileage))

    def update_car(self, car_id, brand, model, year, mileage):
        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")
        with self.connect() as con:
            con.execute(
                """UPDATE cars SET brand=?, model=?, year=?, mileage=? WHERE id=?""",
                (brand, model, year, mileage, car_id)
            )

    def set_mileage(self, car_id, mileage):
        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")
        with self.connect() as con:
            current = con.execute(
                "SELECT mileage FROM cars WHERE id=?", (car_id,)
            ).fetchone()
            if current is None:
                raise ValueError("Автомобиль не найден")
            if mileage < current["mileage"]:
                raise ValueError("Новый пробег меньше сохранённого")
            con.execute("UPDATE cars SET mileage=? WHERE id=?", (mileage, car_id))

    def delete_car(self, car_id):
        with self.connect() as con:
            con.execute("DELETE FROM cars WHERE id=?", (car_id,))

    def add_record(self, car_id, service, when, mileage, days, km, note):
        with self.connect() as con:
            con.execute("""INSERT INTO records
                (car_id,service_type,service_date,mileage,interval_days,interval_km,note)
                VALUES(?,?,?,?,?,?,?)""", (car_id,service,when,mileage,days,km,note))

    def records(self, car_id=None):
        sql = """SELECT r.*,c.brand,c.model FROM records r
                 JOIN cars c ON c.id=r.car_id"""
        args = ()
        if car_id is not None:
            sql += " WHERE r.car_id=?"
            args = (car_id,)
        sql += " ORDER BY r.service_date DESC,r.id DESC"
        with self.connect() as con:
            rows = con.execute(sql, args).fetchall()
        result = []
        for r in rows:
            result.append({
                "id":r["id"], "car_id":r["car_id"], "service":r["service_type"],
                "date":date.fromisoformat(r["service_date"]).strftime("%d.%m.%Y"),
                "mileage":r["mileage"], "note":r["note"] or "",
                "brand":r["brand"], "model":r["model"]
            })
        return result

    def due(self, car_id, mileage_now):
        today = date.today()
        with self.connect() as con:
            rows = con.execute("""
                SELECT r.* FROM records r
                WHERE r.car_id=?
                  AND r.id = (
                    SELECT r2.id FROM records r2
                    WHERE r2.car_id=r.car_id
                      AND r2.service_type=r.service_type
                    ORDER BY r2.service_date DESC, r2.id DESC
                    LIMIT 1
                  )
                ORDER BY r.service_date DESC, r.id DESC
            """, (car_id,)).fetchall()
        items = []
        for r in rows:
            last = date.fromisoformat(r["service_date"])
            due_date = last + timedelta(days=r["interval_days"]) if r["interval_days"] else None
            due_km = r["mileage"] + r["interval_km"] if r["interval_km"] else None
            parts = []
            overdue = False
            if due_date:
                delta = (due_date-today).days
                parts.append("срок наступил" if delta <= 0 else f"через {delta} дн.")
                overdue |= delta <= 0
            if due_km is not None:
                remain = due_km-mileage_now
                parts.append("пробег достигнут" if remain <= 0 else f"через {remain:,} км".replace(",", " "))
                overdue |= remain <= 0
            if parts:
                items.append({"service":r["service_type"],"status":"  •  ".join(parts),"overdue":overdue})
        return items

    def delete_record(self, record_id):
        with self.connect() as con:
            con.execute("DELETE FROM records WHERE id=?", (record_id,))

        # Добавление расхода
    def add_expense(self, car_id, category, when, amount, mileage, note=""):
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")

        if mileage < 0:
            raise ValueError("Пробег не может быть отрицательным")

        with self.connect() as con:
            con.execute("""
                INSERT INTO expenses
                (car_id, category, expense_date, amount, mileage, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (car_id, category, when, amount, mileage, note))

    # Получение расходов
    def expenses(self, car_id=None):
        sql = """
            SELECT e.*, c.brand, c.model
            FROM expenses e
            JOIN cars c ON c.id = e.car_id
        """

        args = ()

        if car_id is not None:
            sql += " WHERE e.car_id=?"
            args = (car_id,)

        sql += " ORDER BY e.expense_date DESC, e.id DESC"

        with self.connect() as con:
            rows = con.execute(sql, args).fetchall()

        return [
            {
                "id": r["id"],
                "car_id": r["car_id"],
                "category": r["category"],
                "date": date.fromisoformat(r["expense_date"]).strftime("%d.%m.%Y"),
                "amount": r["amount"],
                "mileage": r["mileage"],
                "note": r["note"] or "",
                "brand": r["brand"],
                "model": r["model"]
            }
            for r in rows
        ]

    # Общая сумма расходов
    def expense_total(self, car_id=None):
        sql = "SELECT SUM(amount) FROM expenses"
        args = ()

        if car_id is not None:
            sql += " WHERE car_id=?"
            args = (car_id,)

        with self.connect() as con:
            result = con.execute(sql, args).fetchone()[0]

        return result or 0

    # Удаление расхода
    def delete_expense(self, expense_id):
        with self.connect() as con:
            con.execute(
                "DELETE FROM expenses WHERE id=?",
                (expense_id,)
            )
