
from models.participant import Participant


class ParticipantRepository:

    def __init__(self, database):
        self.database = database

    def save(self, participant):
        connection = self.database.connect()
        try:
            connection.execute("""
                INSERT INTO participants (
                    participant_id, name, email, access_code
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(participant_id) DO UPDATE SET
                    name = excluded.name,
                    email = excluded.email,
                    access_code = COALESCE(
                        excluded.access_code,
                        participants.access_code
                    )
            """, (
                participant.participant_id,
                participant.name,
                participant.email,
                participant.access_code
            ))
            connection.commit()
        finally:
            connection.close()

    def get_or_create_by_email(self, name, email, new_access_code):
        """Atomically retrieve or create a participant."""

        connection = self.database.connect()

        try:
            connection.execute("BEGIN IMMEDIATE")

            row = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                WHERE lower(email) = lower(?)
            """, (email.strip(),)).fetchone()

            generated_code = None

            if row is None:
                cursor = connection.execute("""
                    INSERT INTO participants (
                        name, email, access_code
                    )
                    VALUES (?, ?, ?)
                """, (
                    name.strip(),
                    email.strip().lower(),
                    new_access_code
                ))

                participant_id = cursor.lastrowid
                generated_code = new_access_code

            else:
                participant_id = row[0]

                if not row[3]:
                    connection.execute("""
                        UPDATE participants
                        SET name = ?, access_code = ?
                        WHERE participant_id = ?
                    """, (
                        name.strip(),
                        new_access_code,
                        participant_id
                    ))

                    generated_code = new_access_code

                else:
                    connection.execute("""
                        UPDATE participants
                        SET name = ?
                        WHERE participant_id = ?
                    """, (name.strip(), participant_id))

            saved_row = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                WHERE participant_id = ?
            """, (participant_id,)).fetchone()

            connection.commit()

            return Participant(*saved_row), generated_code

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def get_by_id(self, participant_id):
        connection = self.database.connect()
        try:
            row = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                WHERE participant_id = ?
            """, (participant_id,)).fetchone()
        finally:
            connection.close()

        return None if row is None else Participant(*row)

    def get_by_email(self, email):
        connection = self.database.connect()
        try:
            row = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                WHERE lower(email) = lower(?)
            """, (email.strip(),)).fetchone()
        finally:
            connection.close()

        return None if row is None else Participant(*row)

    def get_by_email_and_access_code(self, email, access_code):
        """Find a participant using their email and private access code."""

        if not email or not access_code:
            return None

        connection = self.database.connect()
        try:
            row = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                WHERE lower(email) = lower(?)
                AND upper(access_code) = upper(?)
            """, (email.strip(), access_code.strip())).fetchone()
        finally:
            connection.close()

        return None if row is None else Participant(*row)

    def get_all(self):
        connection = self.database.connect()
        try:
            rows = connection.execute("""
                SELECT participant_id, name, email, access_code
                FROM participants
                ORDER BY participant_id
            """).fetchall()
        finally:
            connection.close()

        return [Participant(*row) for row in rows]

    def get_next_id(self):
        connection = self.database.connect()
        try:
            return connection.execute(
                "SELECT COALESCE(MAX(participant_id), 0) + 1 "
                "FROM participants"
            ).fetchone()[0]
        finally:
            connection.close()
