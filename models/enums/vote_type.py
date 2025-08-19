from enum import Enum

class VoteType(Enum):
    ACCEPT = 'accept'
    REJECT = 'reject'


    def __str__(self):
        return self.value