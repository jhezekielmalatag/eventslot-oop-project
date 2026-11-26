from models.event import Event


class EventRepository:

    def __init__(self, database):
        self.database = database

    @staticmethod
    def _event_from_row(row):
        event = Event(
            event_id=row[0],
            name=row[1],
            location=row[2],
            capacity=row[3],
            status=row[4],
            event_time=row[5],
            description=row[6]
        )
        event.registered_count = row[7]
        return event

    def save(self, event):
        connection = self.database.connect()
        try:
            connection.execute("""
                INSERT INTO events
                (event_id, name, location, capacity, status, event_time, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO UPDATE SET
                    name = excluded.name,
                    location = excluded.location,
                    capacity = excluded.capacity,
                    status = excluded.status,
                    event_time = excluded.event_time,
                    description = excluded.description
            """, (
                event.event_id, event.name, event.location, event.capacity,
                event.status, event.event_time, event.description
            ))
            connection.commit()
        finally:
            connection.close()

    def get_by_id(self, event_id):
        connection = self.database.connect()
        try:
            row = connection.execute("""
                SELECT e.event_id, e.name, e.location, e.capacity, e.status,
                       e.event_time, e.description,
                       (SELECT COUNT(*) FROM registrations r
                        WHERE r.event_id = e.event_id AND r.status = 'confirmed')
                FROM events e WHERE e.event_id = ?
            """, (event_id,)).fetchone()
        finally:
            connection.close()
        return None if row is None else self._event_from_row(row)

    def get_all(self):
        connection = self.database.connect()
        try:
            rows = connection.execute("""
                SELECT e.event_id, e.name, e.location, e.capacity, e.status,
                       e.event_time, e.description,
                       (SELECT COUNT(*) FROM registrations r
                        WHERE r.event_id = e.event_id AND r.status = 'confirmed')
                FROM events e ORDER BY e.event_id
            """).fetchall()
        finally:
            connection.close()
        return [self._event_from_row(row) for row in rows]

    def update(self, event):
        connection = self.database.connect()
        try:
            cursor = connection.execute("""
                UPDATE events
                SET name = ?, location = ?, capacity = ?, status = ?,
                    event_time = ?, description = ?
                WHERE event_id = ?
            """, (
                event.name, event.location, event.capacity, event.status,
                event.event_time, event.description, event.event_id
            ))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
