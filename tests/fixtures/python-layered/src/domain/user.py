# tests/fixtures/python-layered/src/domain/user.py
# VIOLATION: domain layer must not import from infrastructure
from infrastructure.db import UserTable  # <- forbidden import

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def save(self):
        # VIOLATION: domain directly uses DB
        UserTable.insert(self.id, self.name)
