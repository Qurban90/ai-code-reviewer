"""Main entry point."""
from utils import format_output
from db import get_user
from models import User


def run():
    user = get_user(1)
    print(format_output(user))


if __name__ == "__main__":
    run()