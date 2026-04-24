def find_user(cursor, username: str):
    cursor.execute("SELECT id, name FROM users WHERE name = ?", (username,))
    return cursor.fetchone()

