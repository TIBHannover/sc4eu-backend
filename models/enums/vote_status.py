from enum import Enum

class VoteStatus(Enum):
    UNDER_AGREEMENT = "under_agreement"
    UNDER_REVISION = "under_revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"

    def __str__(self):
        return self.value