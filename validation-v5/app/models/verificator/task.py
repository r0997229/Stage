from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from app.models.verificator.enums import TaskStatus

@dataclass
class Task:
    title: str

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    assignee_id: Optional[UUID] = None
    suggestion_id: Optional[UUID] = None
    status: TaskStatus = TaskStatus.OPEN

    is_locked: bool = False                # ← nieuw
    locked_by: Optional[UUID] = None       # ← nieuw: user_id die de lock houdt
    locked_at: Optional[datetime] = None   # ← nieuw