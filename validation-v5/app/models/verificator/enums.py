from enum import Enum

class SuggestionStatus(str, Enum):
    UNREAD      = "unread"
    VIEWED      = "viewed"
    IN_PROGRESS = "in_progress"
    VALIDATED   = "validated"
    TO_DELETE   = "to_delete"

class TaskStatus(str, Enum):
    OPEN        = "open"
    IN_PROGRESS = "in_progress"
    DONE        = "done"

class UserRole(str, Enum):
    ADMIN    = "admin"
    AUTHOR   = "author"
    REVIEWER = "reviewer"

class Space(str, Enum):             # ← nieuw
    DRAFTS    = "drafts"            # Niet-gevalideerde suggesties
    WORKSPACE = "workspace"         # Gevalideerde suggesties
    TRASH     = "trash"             # Verwijderde suggesties