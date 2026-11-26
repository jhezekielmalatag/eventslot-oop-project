from models.registration import Registration
from models.participant import Participant
from models.event import Event


class RegistrationRepository:

    def __init__(self, database):
        self.database = database

    def save(self, registration):
        connection = self.database.connect()
        try:
            connection.execute("""
                INSERT INTO registrations (registration_id, participant_id, event_id, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(registration_id) DO UPDATE SET
                    participant_id = excluded.participant_id,
                    event_id = excluded.event_id,
                    status = excluded.status
            """, (
                registration.registration_id,
                registration.participant.participant_id,
                registration.event.event_id,
                registration.status
            ))
            connection.commit()
        finally:
            connection.close()

    def create_with_capacity(self, registration):
        """Atomically reserve a slot or place the participant in the waitlist."""
        connection = self.database.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            event_row = connection.execute(
                "SELECT capacity, status FROM events WHERE event_id = ?",
                (registration.event.event_id,)
            ).fetchone()
            if event_row is None:
                raise ValueError("Event not found.")
            capacity, event_status = event_row
            if event_status == "cancelled":
                raise ValueError("Cannot register for a cancelled event.")

            duplicate = connection.execute("""
                SELECT 1 FROM registrations
                WHERE participant_id = ? AND event_id = ?
                AND status IN ('confirmed', 'waiting') LIMIT 1
            """, (
                registration.participant.participant_id,
                registration.event.event_id
            )).fetchone()
            if duplicate:
                raise ValueError("You already have an active registration for this event.")

            confirmed_count = connection.execute(
                "SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = 'confirmed'",
                (registration.event.event_id,)
            ).fetchone()[0]
            registration.status = "confirmed" if confirmed_count < capacity else "waiting"
            registration.registration_id = connection.execute(
                "SELECT COALESCE(MAX(registration_id), 0) + 1 FROM registrations"
            ).fetchone()[0]
            connection.execute("""
                INSERT INTO registrations (registration_id, participant_id, event_id, status)
                VALUES (?, ?, ?, ?)
            """, (
                registration.registration_id,
                registration.participant.participant_id,
                registration.event.event_id,
                registration.status
            ))
            connection.commit()
            return registration.status
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _row_to_registration(self, row):
        participant = Participant(row[2], row[3], row[4], row[5])
        event = Event(row[6], row[7], row[8], row[9], row[10], row[11], row[12])
        return Registration(row[0], participant, event, row[1])

    def get_by_id(self, registration_id):
        connection = self.database.connect()
        try:
            row = connection.execute("""
                SELECT r.registration_id, r.status,
                       p.participant_id, p.name, p.email, p.access_code,
                       e.event_id, e.name, e.location, e.capacity,
                       e.status, e.event_time, e.description
                FROM registrations r
                JOIN participants p ON r.participant_id = p.participant_id
                JOIN events e ON r.event_id = e.event_id
                WHERE r.registration_id = ?
            """, (registration_id,)).fetchone()
        finally:
            connection.close()
        return None if row is None else self._row_to_registration(row)

    def get_all(self):
        connection = self.database.connect()
        try:
            ids = connection.execute(
                "SELECT registration_id FROM registrations ORDER BY registration_id"
            ).fetchall()
        finally:
            connection.close()
        return [r for (registration_id,) in ids if (r := self.get_by_id(registration_id)) is not None]

    def get_by_event(self, event_id):
        return [r for r in self.get_all() if r.event.event_id == event_id]

    def get_by_participant_id(self, participant_id):
        return [r for r in self.get_all() if r.participant.participant_id == participant_id]

    def get_next_id(self):
        connection = self.database.connect()
        try:
            return connection.execute(
                "SELECT COALESCE(MAX(registration_id), 0) + 1 FROM registrations"
            ).fetchone()[0]
        finally:
            connection.close()
