
from models.event_request import EventRequest


class EventRequestRepository:

    COLUMNS = """
        request_id,
        applicant_name,
        email,
        organization,
        event_name,
        location,
        event_time,
        purpose,
        status,
        admin_feedback,
        tracking_code
    """

    def __init__(self, database):
        self.database = database

    def _to_event_request(self, row):

        if row is None:
            return None

        return EventRequest(
            request_id=row[0],
            applicant_name=row[1],
            email=row[2],
            organization=row[3],
            event_name=row[4],
            location=row[5],
            purpose=row[7],
            status=row[8],
            admin_feedback=row[9],
            tracking_code=row[10],
            event_time=row[6]
        )

    def save(self, event_request):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO event_requests (
                request_id,
                applicant_name,
                email,
                organization,
                event_name,
                location,
                event_time,
                purpose,
                status,
                admin_feedback,
                tracking_code
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_request.request_id,
            event_request.applicant_name,
            event_request.email,
            event_request.organization,
            event_request.event_name,
            event_request.location,
            event_request.event_time,
            event_request.purpose,
            event_request.status,
            event_request.admin_feedback,
            event_request.tracking_code
        ))

        connection.commit()
        connection.close()

    def get_all(self):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT {self.COLUMNS}
            FROM event_requests
            ORDER BY request_id ASC
        """)

        rows = cursor.fetchall()
        connection.close()

        return [
            self._to_event_request(row)
            for row in rows
        ]

    def get_by_id(self, request_id):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT {self.COLUMNS}
            FROM event_requests
            WHERE request_id = ?
        """, (request_id,))

        row = cursor.fetchone()
        connection.close()

        return self._to_event_request(row)

    def get_by_tracking_details(self, request_id, tracking_code):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT {self.COLUMNS}
            FROM event_requests
            WHERE request_id = ?
            AND tracking_code = ?
        """, (
            request_id,
            tracking_code
        ))

        row = cursor.fetchone()
        connection.close()

        return self._to_event_request(row)

    def update(self, event_request):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE event_requests
            SET
                status = ?,
                admin_feedback = ?
            WHERE request_id = ?
        """, (
            event_request.status,
            event_request.admin_feedback,
            event_request.request_id
        ))

        connection.commit()
        connection.close()

    def get_by_email(self, email):

        connection = self.database.connect()
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT {self.COLUMNS}
            FROM event_requests
            WHERE LOWER(email) = LOWER(?)
            ORDER BY request_id DESC
        """, (email.strip(),))

        rows = cursor.fetchall()
        connection.close()

        return [
            self._to_event_request(row)
            for row in rows
        ]
