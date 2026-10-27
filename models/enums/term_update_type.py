from enum import Enum


class TermUpdateType(Enum):
    CREATE = 'Create'
    UPDATE = 'Update'
    Delete = 'Delete'


    def __str__(self):
        return self.value

    @classmethod
    def is_valid(cls, term_update_type):
        try:
            cls(term_update_type)
            return True
        except ValueError:
            return False

    @classmethod
    def get_valid_options(cls):
        return [item.value for item in cls]