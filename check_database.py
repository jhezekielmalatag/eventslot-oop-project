
import sqlite3

connection = sqlite3.connect("eventslot.db")
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(event_requests)")

for column in cursor.fetchall():
    print(column[1])

connection.close()
