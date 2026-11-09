import unittest

from models.event import Event
from models.participant import Participant
from services.registration_service import RegistrationService


class TestRegistrationService(unittest.TestCase):

    def setUp(self):
        self.event = Event(1, "Python Workshop", "Manila", 1)

        self.participant = Participant(
            1, "Juan Dela Cruz", "juan@example.com"
        )

        self.service = RegistrationService()

    def test_successful_registration(self):
        registration = self.service.register_participant(
            self.participant, self.event
        )

        self.assertEqual(registration.status, "confirmed")

    def test_event_count_increases(self):
        self.service.register_participant(
            self.participant, self.event
        )

        self.assertEqual(self.event.registered_count, 1)

    def test_registration_is_saved(self):
        self.service.register_participant(
            self.participant, self.event
        )

        self.assertEqual(len(self.service.registrations), 1)

    def test_registration_id_increases(self):
        registration = self.service.register_participant(
            self.participant, self.event
        )

        self.assertEqual(registration.registration_id, 1)
        self.assertEqual(self.service.next_registration_id, 2)

    def test_cannot_register_when_event_is_full(self):
        self.service.register_participant(
            self.participant, self.event
        )

        another_participant = Participant(
            2, "Maria Santos", "maria@example.com"
        )

        with self.assertRaises(ValueError):
            self.service.register_participant(
                another_participant, self.event
            )

        self.assertEqual(self.event.registered_count, 1)


if __name__ == "__main__":
    unittest.main()