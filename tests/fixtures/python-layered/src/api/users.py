# tests/fixtures/python-layered/src/api/users.py
# VIOLATION: 9 public route handlers (threshold: 7)
# VIOLATION: list endpoints have no pagination parameters
from fastapi import APIRouter

router = APIRouter(prefix="/v1/users")

@router.get("/")
def list_users():           # VIOLATION: no limit/offset/page param
    return []

@router.get("/{id}")
def get_user(id: int):
    return {}

@router.post("/")
def create_user(body: dict):
    return {}

@router.put("/{id}")
def update_user(id: int, body: dict):
    return {}

@router.delete("/{id}")
def delete_user(id: int):
    return {}

@router.get("/{id}/orders")
def list_user_orders(id: int):  # VIOLATION: no pagination
    return []

@router.post("/{id}/activate")
def activate_user(id: int):
    return {}

@router.post("/{id}/deactivate")
def deactivate_user(id: int):
    return {}

@router.get("/{id}/profile")
def get_profile(id: int):
    return {}
# 9 route handlers = fat controller
