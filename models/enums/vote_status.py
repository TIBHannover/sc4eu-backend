from enum import Enum

class VoteStatus(Enum):
    UNDER_AGREEMENT = "under_agreement"
    UNDER_REVISION = "under_revision"
    ACCEPT = "accept"
    NOT_ACCEPT = "not accept"
    DRAFT = "draft"
    CLOSED = "closed"

    def __str__(self):
        return self.value