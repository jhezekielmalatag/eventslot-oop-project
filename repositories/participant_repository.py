
from models.participant import Participant


class ParticipantRepository:

    def __init__(self, database):
        self.database = database

    def save(self, participant):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO participants
            (participant_id, name, email)
            VALUES (?, ?, ?)
            ON CONFLICT(participant_id) DO UPDATE SET
                name = excluded.name,
                email = excluded.email
        """, (
            participant.participant_id,
            participant.name,
            participant.email
        ))

        connection.commit()
        connection.close()

    def get_by_id(self, participant_id):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT participant_id, name, email
            FROM participants
            WHERE participant_id = ?
        """, (participant_id,))

        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None

        return Participant(
            participant_id=row[0],
            name=row[1],
            email=row[2]
        )

    def get_all(self):
        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT participant_id, name, email
            FROM participants
            ORDER BY participant_id
        """)

        rows = cursor.fetchall()
        connection.close()

        participants = []

        for row in rows:
            participant = Participant(
                participant_id=row[0],
                name=row[1],
                email=row[2]
            )

            participants.append(participant)

        return participants
