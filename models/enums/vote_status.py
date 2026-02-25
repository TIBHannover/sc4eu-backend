from enum import Enum

class VoteStatus(Enum):
    UNDER_AGREEMENT = "under_agreement"
    UNDER_REVISION = "under_revision"
    ACCEPT = "accept"
    NOT_ACCEPT = "not accept"
    CLOSED = "closed"
    DRAFT = "draft"
    
    def __str__(self):
        return self.value
    
    @classmethod
    def is_valid(cls, status):
        try:
            cls(status)
            return True
        except ValueError:
            return False

    @classmethod
    def get_valid_options(cls):
        return [item.value for item in cls]

    @staticmethod
    def to_string():
        return ', '.join(VoteStatus.get_valid_options())