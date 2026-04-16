from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.models.verificator.enums import UserRole  # ← nieuw

@dataclass
class User:
    name: str
    email: str

    id: UUID = field(default_factory=uuid4)

    role: UserRole = UserRole.AUTHOR