
from models.registration import Registration
from models.participant import Participant
from models.event import Event


class RegistrationRepository:

    def __init__(self, database):
        self.database = database

    def save(self, registration):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO registrations
            (registration_id, participant_id, event_id, status)
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
        connection.close()

    def get_by_id(self, registration_id):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                r.registration_id,
                r.status,
                p.participant_id,
                p.name,
                p.email,
                e.event_id,
                e.name,
                e.location,
                e.capacity
            FROM registrations r
            JOIN participants p
                ON r.participant_id = p.participant_id
            JOIN events e
                ON r.event_id = e.event_id
            WHERE r.registration_id = ?
        """, (registration_id,))

        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None

        participant = Participant(
            row[2], row[3], row[4]
        )

        event = Event(
            row[5], row[6], row[7], row[8]
        )

        return Registration(
            row[0], participant, event, row[1]
        )

    def get_all(self):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT registration_id
            FROM registrations
            ORDER BY registration_id
        """)

        rows = cursor.fetchall()
        connection.close()

        registrations = []

        for row in rows:
            registration = self.get_by_id(row[0])

            if registration is not None:
                registrations.append(registration)

        return registrations
