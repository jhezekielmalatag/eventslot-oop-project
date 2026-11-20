
import sqlite3


class Database:

    def __init__(self, database_name="eventslot.db"):
        self.database_name = database_name

    def connect(self):
        connection = sqlite3.connect(self.database_name)
        return connection

    def create_tables(self):
        connection = self.connect()
        cursor = connection.cursor()

        # Create the events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'active'
            )
        """)

        # Add status to an existing events table if needed
        cursor.execute("PRAGMA table_info(events)")
        columns = [column[1] for column in cursor.fetchall()]

        if "status" not in columns:
            cursor.execute("""
                ALTER TABLE events
                ADD COLUMN status TEXT NOT NULL DEFAULT 'active'
            """)

        # Create the participants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                participant_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

        # Create the registrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id INTEGER PRIMARY KEY,
                participant_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',

                FOREIGN KEY (participant_id)
                    REFERENCES participants(participant_id),

                FOREIGN KEY (event_id)
                    REFERENCES events(event_id)
            )
        """)

        connection.commit()
        connection.close()
