def find_user(cursor, username: str):
    query = f"SELECT id, name FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

