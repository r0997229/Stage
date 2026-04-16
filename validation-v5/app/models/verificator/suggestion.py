from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from app.models.verificator.enums import SuggestionStatus, Space  # ← Space nieuw

@dataclass
class Suggestion:
    title: str
    description: str
    project_id: UUID
    section: str = ""
    source: str = ""                                # ← nieuw: exacte kopie uit het document

    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: SuggestionStatus = SuggestionStatus.UNREAD
    space: Space = Space.DRAFTS
    deleted_at: Optional[datetime] = None