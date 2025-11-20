from enum import Enum

class UserRole(str, Enum):
    """Enum which enforces valid role names for API input."""
    admin = "admin"
    user = "user"