from enum import Enum

class UserRole(Enum):
    PUBLIC_USER = "public_user"
    MEMBER = "member"
    PROJECT_ADMIN = "project_admin"
    ADMIN = "admin"
    SYSTEM_ADMIN = "system_admin"

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
        return ', '.join(UserRole.get_valid_options())