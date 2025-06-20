from enum import StrEnum
from typing import List

class UserRole(StrEnum):
    """Базовые роли пользователей"""
    USER = "user"
    ADMIN = "admin"
    
    @classmethod
    def get_all_roles(cls) -> List[str]:
        """Получить все доступные роли"""
        return [role.value for role in cls]