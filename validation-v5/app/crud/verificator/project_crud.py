from uuid import UUID
from app.models.verificator.project import Project
from app.crud.verificator.user_crud import UserCRUD

_store: dict[UUID, Project] = {}


class ProjectCRUD:

    @staticmethod
    def create(title: str, owner_id: UUID) -> Project:
        u = UserCRUD.get(owner_id)
        if u is None:
            raise ValueError(f"User {owner_id} bestaat niet.")

        p = Project(title=title, owner_id=owner_id)
        _store[p.id] = p
        return p

    @staticmethod
    def get(id: UUID) -> Project | None:
        return _store.get(id)

    @staticmethod
    def list_all() -> list[Project]:
        return list(_store.values())

    @staticmethod
    def update(id: UUID, title: str = None) -> Project:
        p = _store[id]
        if title: p.title = title
        return p

    @staticmethod
    def delete(id: UUID) -> None:
        _store.pop(id, None)