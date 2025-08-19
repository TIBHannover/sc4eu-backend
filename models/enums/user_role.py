from enum import Enum

class UserRole(Enum):
    PUBLIC_USER = "public_user"
    MEMBER = "member"
    PROJECT_ADMIN = "project_admin"
    ADMIN = "admin"
    SYSTEM_ADMIN = "system_admin"

    def __str__(self):
        return self.value
