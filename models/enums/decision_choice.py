from enum import Enum

class DecisionChoice(Enum):
    COMMENT = 'comment'
    APPROVE = 'approved'
    REJECT = 'rejected'

    def __str__(self):
        return self.value
    
    @classmethod
    def is_valid(cls, choice):
        try:
            cls(choice)
            return True
        except ValueError:
            return False

    @classmethod
    def get_valid_options(cls):
        return [item.value for item in cls]

    @staticmethod
    def to_string():
        return ', '.join(DecisionChoice.get_valid_options())
