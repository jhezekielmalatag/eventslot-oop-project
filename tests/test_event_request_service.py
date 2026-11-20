
import unittest
import tempfile
import os

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.event_request_repository import EventRequestRepository

from services.admin_service import AdminService
from services.event_request_service import EventRequestService


class TestEventRequestService(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        database_path = os.path.join(
            self.temp_directory.name,
            "test_eventslot.db"
        )

        self.database = Database(database_path)
        self.database.create_tables()

        self.event_repository = EventRepository(self.database)
        self.registration_repository = RegistrationRepository(
            self.database
        )
        self.event_request_repository = EventRequestRepository(
            self.database
        )

        self.admin_service = AdminService(
            self.event_repository,
            self.registration_repository
        )

        self.service = EventRequestService(
            self.event_request_repository,
            self.admin_service
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def create_sample_request(self):
        return self.service.submit_request(
            applicant_name="Juan Dela Cruz",
            email="juan@example.com",
            organization="Student Council",
            event_name="Technology Seminar",
            location="School Auditorium",
            event_time="02:00 PM",
            purpose="Educational seminar"
        )

    def test_submit_request(self):
        request = self.create_sample_request()

        self.assertEqual(request.request_id, 1)
        self.assertEqual(request.applicant_name, "Juan Dela Cruz")
        self.assertEqual(request.email, "juan@example.com")
        self.assertEqual(request.event_name, "Technology Seminar")
        self.assertEqual(request.event_time, "02:00 PM")
        self.assertEqual(request.purpose, "Educational seminar")
        self.assertEqual(request.status, "Waiting for Approval")

    def test_check_request_status(self):
        request = self.create_sample_request()

        result = self.service.check_request_status(
            request.request_id,
            request.tracking_code
        )

        self.assertEqual(result.status, "Waiting for Approval")

    def test_approve_request(self):
        request = self.create_sample_request()

        event = self.service.approve_request(
            request.request_id,
            capacity=100,
            feedback="Your event request has been approved."
        )

        updated_request = self.event_request_repository.get_by_id(
            request.request_id
        )

        self.assertEqual(updated_request.status, "Accepted")
        self.assertEqual(event.name, "Technology Seminar")
        self.assertEqual(event.capacity, 100)

    def test_reject_request(self):
        request = self.create_sample_request()

        self.service.reject_request(
            request.request_id,
            "Insufficient event information."
        )

        updated_request = self.event_request_repository.get_by_id(
            request.request_id
        )

        self.assertEqual(updated_request.status, "Rejected")
        self.assertEqual(
            updated_request.admin_feedback,
            "Insufficient event information."
        )

    def test_reject_without_feedback(self):
        request = self.create_sample_request()

        with self.assertRaises(ValueError):
            self.service.reject_request(request.request_id)

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            self.service.submit_request(
                applicant_name="Juan Dela Cruz",
                email="invalid-email",
                organization="Student Council",
                event_name="Technology Seminar",
                location="School Auditorium",
                event_time="02:00 PM",
                purpose="Educational seminar"
            )

    def test_missing_event_time(self):
        with self.assertRaises(ValueError):
            self.service.submit_request(
                applicant_name="Juan Dela Cruz",
                email="juan@example.com",
                organization="Student Council",
                event_name="Technology Seminar",
                location="School Auditorium",
                event_time="",
                purpose="Educational seminar"
            )

    def test_cannot_approve_twice(self):
        request = self.create_sample_request()

        self.service.approve_request(request.request_id, 100)

        with self.assertRaises(ValueError):
            self.service.approve_request(request.request_id, 100)


if __name__ == "__main__":
    unittest.main()
