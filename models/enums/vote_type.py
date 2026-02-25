from enum import Enum

class VoteType(Enum):
    ACCEPT = 'accept'
    REJECT = 'reject'


    def __str__(self):
        return self.value

    @classmethod
    def is_valid(cls, vote):
        try:
            cls(vote)
            return True
        except ValueError:
            return False

    @classmethod
    def get_valid_options(cls):
        return [item.value for item in cls]