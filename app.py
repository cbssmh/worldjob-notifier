from db import init_db
from scheduler import start_scheduler


def main():
    init_db()
    start_scheduler()


if __name__ == "__main__":
    main()