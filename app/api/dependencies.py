from fastapi import Request

from app.repositories.memory import MemoryStore


def get_store(request: Request) -> MemoryStore:
    return request.app.state.store
