
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

    def test_registration_is_added_to_waitlist_when_event_is_full(self):
        self.service.register_participant(
            self.participant, self.event
        )

        another_participant = Participant(
            2, "Maria Santos", "maria@example.com"
        )

        registration = self.service.register_participant(
            another_participant, self.event
        )

        self.assertEqual(registration.status, "waiting")
        self.assertEqual(self.event.registered_count, 1)

        waitlist = self.service._get_waitlist(self.event)
        self.assertEqual(len(waitlist), 1)

    def test_cancel_registration_releases_slot(self):
        registration = self.service.register_participant(
            self.participant, self.event
        )

        self.service.cancel_registration(registration)

        self.assertEqual(self.event.registered_count, 0)
        self.assertEqual(self.event.available_slots, 1)
        self.assertEqual(registration.status, "cancelled")

    def test_cannot_cancel_registration_twice(self):
        registration = self.service.register_participant(
            self.participant, self.event
        )

        self.service.cancel_registration(registration)

        with self.assertRaises(ValueError):
            self.service.cancel_registration(registration)

        self.assertEqual(self.event.registered_count, 0)

    def test_cancelling_registration_promotes_first_waiting_participant(self):
        # Juan takes the only available slot
        juan_registration = self.service.register_participant(
            self.participant, self.event
        )

        # Maria joins the waitlist
        maria = Participant(2, "Maria Santos", "maria@example.com")
        maria_registration = self.service.register_participant(
            maria, self.event
        )

        # Pedro joins after Maria
        pedro = Participant(3, "Pedro Reyes", "pedro@example.com")
        pedro_registration = self.service.register_participant(
            pedro, self.event
        )

        # Check the waitlist before cancellation
        print("\nBefore cancellation:")
        print("Juan:", juan_registration.status)
        print("Maria:", maria_registration.status)
        print("Pedro:", pedro_registration.status)
        print("Waitlist:", len(self.service._get_waitlist(self.event)))

        # Juan cancels
        self.service.cancel_registration(juan_registration)

        # Check the result
        print("\nAfter cancellation:")
        print("Juan:", juan_registration.status)
        print("Maria:", maria_registration.status)
        print("Pedro:", pedro_registration.status)
        print("Waitlist:", len(self.service._get_waitlist(self.event)))

        # Verify FIFO promotion
        self.assertEqual(juan_registration.status, "cancelled")
        self.assertEqual(maria_registration.status, "confirmed")
        self.assertEqual(pedro_registration.status, "waiting")
        self.assertEqual(self.event.registered_count, 1)
        
    def test_cancelling_waiting_registration_removes_them_from_waitlist(self):
        # Juan occupies the only available slot
        self.service.register_participant(
            self.participant, self.event
        )
        
        # Maria joins the waitlist
        maria = Participant(2, "Maria Santos", "maria@example.com")
        maria_registration = self.service.register_participant(
            maria, self.event
        )

        # Maria cancels
        self.service.cancel_registration(maria_registration)

        # Verify the results
        waitlist = self.service._get_waitlist(self.event)

        self.assertEqual(maria_registration.status, "cancelled")
        self.assertEqual(len(waitlist), 0)
        self.assertEqual(self.event.registered_count, 1)



if __name__ == "__main__":
    unittest.main()
