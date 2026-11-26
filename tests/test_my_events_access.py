import os
import unittest

from models.event import Event
from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.participant_repository import ParticipantRepository
from repositories.registration_repository import RegistrationRepository
from services.registration_service import RegistrationService


class TestMyEventsAccess(unittest.TestCase):

    def setUp(self):
        self.database_name = "test_my_events_access.db"
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.database = Database(self.database_name)
        self.database.create_tables()
        self.events = EventRepository(self.database)
        self.participants = ParticipantRepository(self.database)
        self.registrations = RegistrationRepository(self.database)
        self.service = RegistrationService(
            self.events, self.participants, self.registrations
        )

    def tearDown(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def test_new_participant_receives_access_code_and_can_view_events(self):
        event = Event(1, "Python Workshop", "Library", 5)
        registration = self.service.register_by_details(
            "Juan Dela Cruz", "juan@example.com", event
        )

        code = self.service.last_generated_access_code
        self.assertIsNotNone(code)
        self.assertEqual(len(code), 8)

        participant = self.participants.get_by_email_and_access_code(
            "JUAN@example.com", code.lower()
        )
        self.assertIsNotNone(participant)
        self.assertEqual(participant.name, "Juan Dela Cruz")

        records = self.registrations.get_by_participant_id(
            participant.participant_id
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].registration_id, registration.registration_id)

    def test_wrong_access_code_does_not_retrieve_participant(self):
        self.service.register_by_details(
            "Maria Santos", "maria@example.com",
            Event(1, "Design Seminar", "Hall A", 5)
        )
        self.assertIsNone(
            self.participants.get_by_email_and_access_code(
                "maria@example.com", "WRONG123"
            )
        )

    def test_my_events_shows_fifo_promotion_after_cancellation(self):
        event = Event(1, "OOP Seminar", "Auditorium", 1)
        first = self.service.register_by_details(
            "First Person", "first@example.com", event
        )
        self.service.register_by_details(
            "Second Person", "second@example.com", event
        )
        second_code = self.service.last_generated_access_code

        self.service.cancel_registration(first)

        second_participant = self.participants.get_by_email_and_access_code(
            "second@example.com", second_code
        )
        records = self.registrations.get_by_participant_id(
            second_participant.participant_id
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, "confirmed")


if __name__ == "__main__":
    unittest.main()
