"""Database layer."""
from sample_project.models import User


def get_user(user_id: int) -> User:
    return User(id=user_id, name=f"User-{user_id}")