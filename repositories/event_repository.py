
from models.event import Event


class EventRepository:

    def __init__(self, database):
        self.database = database

    def save(self, event):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO events
            (event_id, name, location, capacity, status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(event_id) DO UPDATE SET
                name = excluded.name,
                location = excluded.location,
                capacity = excluded.capacity,
                status = excluded.status
        """, (
            event.event_id,
            event.name,
            event.location,
            event.capacity,
            event.status
        ))

        connection.commit()
        connection.close()

    def get_by_id(self, event_id):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT event_id, name, location, capacity, status
            FROM events
            WHERE event_id = ?
        """, (event_id,))

        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None

        return Event(
            event_id=row[0],
            name=row[1],
            location=row[2],
            capacity=row[3],
            status=row[4]
        )

    def get_all(self):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT event_id, name, location, capacity, status
            FROM events
            ORDER BY event_id
        """)

        rows = cursor.fetchall()
        connection.close()

        events = []

        for row in rows:
            event = Event(
                event_id=row[0],
                name=row[1],
                location=row[2],
                capacity=row[3],
                status=row[4]
            )

            events.append(event)

        return events

    def update(self, event):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE events
            SET name = ?,
                location = ?,
                capacity = ?,
                status = ?
            WHERE event_id = ?
        """, (
            event.name,
            event.location,
            event.capacity,
            event.status,
            event.event_id
        ))

        updated = cursor.rowcount > 0

        connection.commit()
        connection.close()

        return updated
