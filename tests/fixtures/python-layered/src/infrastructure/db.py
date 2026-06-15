# tests/fixtures/python-layered/src/infrastructure/db.py
class UserTable:
    @staticmethod
    def insert(user_id: int, name: str) -> None:
        print(f"INSERT users VALUES ({user_id}, '{name}')")

    @staticmethod
    def find(user_id: int) -> dict:
        return {"id": user_id, "name": "stub"}
