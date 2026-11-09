import unittest
from models.event import Event
from models.participant import Participant
from models.registration import Registration


class TestRegistration(unittest.TestCase):

    def setUp(self):
        self.event = Event(1, "Python Workshop", "Manila", 30)
        self.participant = Participant(
            1, "Juan Dela Cruz", "juan@example.com"
        )

        self.registration = Registration(
            1, self.participant, self.event
        )

    def test_registration_creation(self):
        self.assertEqual(self.registration.registration_id, 1)
        self.assertEqual(self.registration.status, "confirmed")

    def test_registration_has_participant(self):
        self.assertIs(self.registration.participant, self.participant)

    def test_registration_has_event(self):
        self.assertIs(self.registration.event, self.event)

    def test_cancel_registration(self):
        self.registration.cancel()
        self.assertEqual(self.registration.status, "cancelled")

    def test_registration_description(self):
        expected = (
            "Registration #1 | Juan Dela Cruz | "
            "Python Workshop | Status: confirmed"
        )
        self.assertEqual(str(self.registration), expected)


if __name__ == "__main__":
    unittest.main()