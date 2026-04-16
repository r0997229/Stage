from uuid import UUID
from datetime import datetime, timedelta
from app.models.verificator.suggestion import Suggestion
from app.models.verificator.task import Task
from app.models.verificator.enums import SuggestionStatus, Space

from app.crud.verificator.project_crud import ProjectCRUD

_store: dict[UUID, Suggestion] = {}


class SuggestionCRUD:

    @staticmethod
    def create(
        title: str,
        description: str,
        project_id: UUID,
        section: str = "",
        source: str = "",
    ) -> Suggestion:
        p = ProjectCRUD.get(project_id)
        if p is None:
            raise ValueError(f"Project {project_id} bestaat niet.")

        s = Suggestion(
            title=title,
            description=description,
            project_id=project_id,
            section=section,
            source=source,
        )
        _store[s.id] = s
        return s

    @staticmethod
    def get(id: UUID) -> Suggestion | None:
        return _store.get(id)

    @staticmethod
    def list_all() -> list[Suggestion]:
        return list(_store.values())

    @staticmethod
    def list_by_project(project_id: UUID) -> list[Suggestion]:
        return [s for s in _store.values() if s.project_id == project_id]

    @staticmethod
    def list_by_space(project_id: UUID, space: Space) -> list[Suggestion]:
        return [
            s for s in _store.values()
            if s.project_id == project_id
            and s.space == space
        ]

    @staticmethod
    def update(id: UUID, title: str = None, description: str = None) -> Suggestion:
        s = _store[id]
        if title:       s.title = title
        if description: s.description = description
        return s

    @staticmethod
    def set_status(suggestion_id: UUID, status: SuggestionStatus) -> Suggestion:
        s = _store[suggestion_id]
        s.status = status
        return s

    @staticmethod
    def move_to_space(suggestion_id: UUID, space: Space) -> Suggestion:
        s = _store[suggestion_id]
        s.space = space
        return s

    @staticmethod
    def validate(suggestion_id: UUID) -> Task:                           # ← nieuw
        # Lokale import om circulaire import te vermijden
        from app.crud.verificator.task_crud import TaskCRUD

        s = _store.get(suggestion_id)
        if s is None:
            raise ValueError(f"Suggestion {suggestion_id} bestaat niet.")

        if s.status == SuggestionStatus.VALIDATED:
            raise ValueError(f"Suggestion {suggestion_id} is al gevalideerd.")

        # Suggestion updaten
        s.status = SuggestionStatus.VALIDATED
        s.space  = Space.WORKSPACE

        # Task aanmaken vanuit de suggestion
        task = Task(
            title=s.title,
            suggestion_id=s.id,
            project_id=s.project_id,
        )

        # Task opslaan via TaskCRUD
        TaskCRUD.save(task)
        return task

    @staticmethod
    def soft_delete(suggestion_id: UUID) -> Suggestion:
        s = _store[suggestion_id]
        s.space      = Space.TRASH
        s.status     = SuggestionStatus.TO_DELETE
        s.deleted_at = datetime.utcnow()
        return s

    @staticmethod
    def restore(suggestion_id: UUID) -> Suggestion:
        s = _store[suggestion_id]
        s.space      = Space.DRAFTS
        s.status     = SuggestionStatus.UNREAD
        s.deleted_at = None
        return s

    @staticmethod
    def delete(id: UUID) -> None:
        _store.pop(id, None)

    @staticmethod
    def purge_expired_trash(days: int = 30) -> int:
        cutoff  = datetime.utcnow() - timedelta(days=days)
        expired = [
            s for s in _store.values()
            if s.space == Space.TRASH
            and s.deleted_at is not None
            and s.deleted_at < cutoff
        ]
        for s in expired:
            _store.pop(s.id)
        return len(expired)