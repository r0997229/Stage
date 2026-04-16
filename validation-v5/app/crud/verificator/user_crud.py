from uuid import UUID
from app.models.verificator.enums import UserRole
from app.models.verificator.user import User

_store: dict[UUID, User] = {}


class UserCRUD:

    @staticmethod
    def create(name: str, email: str, role: UserRole = UserRole.AUTHOR) -> User: 
        u = User(name=name, email=email, role=role)
        _store[u.id] = u
        return u

    @staticmethod
    def get(id: UUID) -> User | None:
        return _store.get(id)

    @staticmethod
    def list_all() -> list[User]:
        return list(_store.values())

    @staticmethod
    def update(id: UUID, name: str = None, email: str = None) -> User:
        u = _store[id]
        if name:  u.name = name
        if email: u.email = email
        return u

    @staticmethod
    def delete(id: UUID) -> None:
        _store.pop(id, None)

    @staticmethod
    def get_or_create_default() -> User:
        for u in _store.values():
            if u.email == "default@app.com":
                return u
        return UserCRUD.create(name="Default", email="default@app.com", role=UserRole.ADMIN)