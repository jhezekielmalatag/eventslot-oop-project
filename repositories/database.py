import secrets
import sqlite3


class Database:

    def __init__(self, database_name="eventslot.db"):
        self.database_name = database_name

    def connect(self):
        connection = sqlite3.connect(self.database_name, timeout=10)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def create_tables(self):
        connection = self.connect()
        try:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    event_time TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL DEFAULT ''
                )
            """)
            cursor.execute("PRAGMA table_info(events)")
            event_columns = {column[1] for column in cursor.fetchall()}
            if "status" not in event_columns:
                cursor.execute("ALTER TABLE events ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
            if "event_time" not in event_columns:
                cursor.execute("ALTER TABLE events ADD COLUMN event_time TEXT NOT NULL DEFAULT ''")
            if "description" not in event_columns:
                cursor.execute("ALTER TABLE events ADD COLUMN description TEXT NOT NULL DEFAULT ''")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    participant_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    access_code TEXT
                )
            """)
            cursor.execute("PRAGMA table_info(participants)")
            participant_columns = {column[1] for column in cursor.fetchall()}
            if "access_code" not in participant_columns:
                cursor.execute("ALTER TABLE participants ADD COLUMN access_code TEXT")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registrations (
                    registration_id INTEGER PRIMARY KEY,
                    participant_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'confirmed',
                    FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
                    FOREIGN KEY (event_id) REFERENCES events(event_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_requests (
                    request_id INTEGER PRIMARY KEY,
                    applicant_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    event_time TEXT NOT NULL DEFAULT '',
                    purpose TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Waiting for Approval',
                    admin_feedback TEXT NOT NULL DEFAULT '',
                    tracking_code TEXT NOT NULL DEFAULT ''
                )
            """)

            cursor.execute("PRAGMA table_info(event_requests)")
            request_columns = {column[1] for column in cursor.fetchall()}
            if "age" in request_columns:
                cursor.execute("ALTER TABLE event_requests RENAME TO event_requests_old")
                cursor.execute("""
                    CREATE TABLE event_requests (
                        request_id INTEGER PRIMARY KEY,
                        applicant_name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        organization TEXT NOT NULL,
                        event_name TEXT NOT NULL,
                        location TEXT NOT NULL,
                        event_time TEXT NOT NULL DEFAULT '',
                        purpose TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'Waiting for Approval',
                        admin_feedback TEXT NOT NULL DEFAULT '',
                        tracking_code TEXT NOT NULL DEFAULT ''
                    )
                """)
                cursor.execute("PRAGMA table_info(event_requests_old)")
                old_columns = {column[1] for column in cursor.fetchall()}
                event_time_value = "event_time" if "event_time" in old_columns else "''"
                feedback_value = "admin_feedback" if "admin_feedback" in old_columns else "''"
                tracking_value = "tracking_code" if "tracking_code" in old_columns else "''"
                cursor.execute(f"""
                    INSERT INTO event_requests (
                        request_id, applicant_name, email, organization,
                        event_name, location, event_time, purpose, status,
                        admin_feedback, tracking_code
                    )
                    SELECT request_id, applicant_name, email, organization,
                        event_name, location, {event_time_value}, purpose,
                        status, {feedback_value}, {tracking_value}
                    FROM event_requests_old
                """)
                cursor.execute("DROP TABLE event_requests_old")
            else:
                if "event_time" not in request_columns:
                    cursor.execute("ALTER TABLE event_requests ADD COLUMN event_time TEXT NOT NULL DEFAULT ''")
                if "tracking_code" not in request_columns:
                    cursor.execute("ALTER TABLE event_requests ADD COLUMN tracking_code TEXT NOT NULL DEFAULT ''")
                if "admin_feedback" not in request_columns:
                    cursor.execute("ALTER TABLE event_requests ADD COLUMN admin_feedback TEXT NOT NULL DEFAULT ''")

            cursor.execute("SELECT request_id FROM event_requests WHERE tracking_code = '' OR tracking_code IS NULL")
            for (request_id,) in cursor.fetchall():
                cursor.execute(
                    "UPDATE event_requests SET tracking_code = ? WHERE request_id = ?",
                    (secrets.token_hex(8).upper(), request_id)
                )

            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_event_requests_tracking_code
                ON event_requests(tracking_code)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_registrations_event_status
                ON registrations(event_id, status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_registrations_participant
                ON registrations(participant_id)
            """)

            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
