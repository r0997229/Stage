from uuid import UUID
from datetime import datetime
from app.models.verificator.task import Task
from app.models.verificator.enums import TaskStatus, UserRole
from app.crud.verificator.user_crud import UserCRUD
from app.crud.verificator.suggestion_crud import SuggestionCRUD

_store: dict[UUID, Task] = {}


class TaskLockedError(Exception):
    pass


class TaskCRUD:

    @staticmethod
    def save(task: Task) -> Task:                        # ← nieuw: enkel opslaan
        _store[task.id] = task
        return task

    @staticmethod
    def create(title: str) -> Task:
        t = Task(title=title)
        _store[t.id] = t
        return t

    @staticmethod
    def create_from_suggestion(suggestion_id: UUID) -> Task:
        s = SuggestionCRUD.get(suggestion_id)
        if s is None:
            raise ValueError(f"Suggestion {suggestion_id} bestaat niet.")
        t = Task(title=s.title, suggestion_id=suggestion_id)
        _store[t.id] = t
        return t

    @staticmethod
    def get(id: UUID) -> Task | None:
        return _store.get(id)

    @staticmethod
    def list_all() -> list[Task]:
        return list(_store.values())

    @staticmethod
    def list_by_project(project_id: UUID) -> list[Task]:
        return [t for t in _store.values() if t.project_id == project_id]

    @staticmethod
    def update(id: UUID, title: str = None) -> Task:
        t = _store[id]
        if title: t.title = title
        return t

    @staticmethod
    def delete(id: UUID) -> None:
        _store.pop(id, None)

    @staticmethod
    def assign(task_id: UUID, user_id: UUID) -> Task:
        t = _store[task_id]
        u = UserCRUD.get(user_id)
        if u is None:
            raise ValueError(f"User {user_id} bestaat niet.")
        t.assignee_id = user_id
        return t

    @staticmethod
    def set_status(task_id: UUID, user_id: UUID, status: TaskStatus) -> Task:
        t = _store[task_id]
        u = UserCRUD.get(user_id)
        if u is None:
            raise ValueError(f"User {user_id} bestaat niet.")
        is_assignee   = t.assignee_id == user_id
        is_privileged = u.role in (UserRole.ADMIN, UserRole.REVIEWER)
        if not is_assignee and not is_privileged:
            raise PermissionError(f"User {user_id} mag deze taak niet wijzigen.")
        t.status = status
        return t

    @staticmethod
    def lock(task_id: UUID, user_id: UUID) -> Task:
        t = _store[task_id]
        if t.is_locked and t.locked_by != user_id:
            raise TaskLockedError(f"Task is al vergrendeld door user {t.locked_by}.")
        t.is_locked = True
        t.locked_by = user_id
        t.locked_at = datetime.utcnow()
        return t

    @staticmethod
    def unlock(task_id: UUID, user_id: UUID, force: bool = False) -> Task:
        t = _store[task_id]
        if not force and t.locked_by != user_id:
            raise TaskLockedError(f"Enkel de eigenaar (user {t.locked_by}) kan ontgrendelen.")
        t.is_locked = False
        t.locked_by = None
        t.locked_at = None
        return t