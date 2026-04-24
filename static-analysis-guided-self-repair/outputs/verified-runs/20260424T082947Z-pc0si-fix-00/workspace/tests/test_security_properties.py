from solution import find_user


class Cursor:
    def __init__(self):
        self.calls = []

    def execute(self, *args):
        self.calls.append(args)

    def fetchone(self):
        return None


def test_find_user_uses_parameterized_query():
    cursor = Cursor()
    find_user(cursor, "alice' OR '1'='1")

    query, params = cursor.calls[0]
    assert "?" in query
    assert "alice' OR '1'='1" not in query
    assert params == ("alice' OR '1'='1",)

