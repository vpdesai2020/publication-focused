from solution import find_user


class Cursor:
    def __init__(self):
        self.calls = []

    def execute(self, *args):
        self.calls.append(args)

    def fetchone(self):
        return (1, "alice")


def test_find_user_returns_first_row():
    cursor = Cursor()
    assert find_user(cursor, "alice") == (1, "alice")
    assert cursor.calls

