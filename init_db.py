import sqlite3
from datetime import datetime

try:
    connection = sqlite3.connect('database.db')

    with open('schema.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    # Use parameterized query and pass a Python datetime object
    cur.execute("INSERT INTO events (eventName, eventDescription, dateEvent) VALUES (?, ?, ?)",
                ('Date of My Birth', 'I was born today!', datetime(2002, 4, 20).strftime('%Y-%m-%d %H:%M:%S')))

    connection.commit()

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    if connection:
        connection.close()
