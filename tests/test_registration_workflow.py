import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.participant_repository import ParticipantRepository
from repositories.registration_repository import RegistrationRepository
from services.admin_service import AdminService
from services.registration_service import RegistrationService


class RegistrationWorkflowTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(os.path.join(self.temp_dir.name, "test.db"))
        self.database.create_tables()
        self.events = EventRepository(self.database)
        self.participants = ParticipantRepository(self.database)
        self.registrations = RegistrationRepository(self.database)
        self.admin = AdminService(self.events, self.registrations)
        self.service = RegistrationService(
            self.events, self.participants, self.registrations
        )
        self.event = self.admin.create_event(
            "Test Event", "Test Venue", 1,
            event_time="09:30 AM", description="A test event"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registration_confirms_when_slot_is_available(self):
        registration = self.service.register_by_details(
            "Alex Participant", "alex@example.com", self.event
        )
        self.assertEqual(registration.status, "confirmed")
        self.assertEqual(self.events.get_by_id(self.event.event_id).registered_count, 1)

    def test_full_event_places_next_participant_on_waitlist(self):
        first = self.service.register_by_details(
            "First Person", "first@example.com", self.event
        )
        second = self.service.register_by_details(
            "Second Person", "second@example.com", self.event
        )
        self.assertEqual(first.status, "confirmed")
        self.assertEqual(second.status, "waiting")

    def test_cancelling_confirmed_registration_promotes_fifo_waiter(self):
        first = self.service.register_by_details(
            "First Person", "first@example.com", self.event
        )
        second = self.service.register_by_details(
            "Second Person", "second@example.com", self.event
        )
        third = self.service.register_by_details(
            "Third Person", "third@example.com", self.event
        )
        self.service.cancel_registration(first)
        saved = {r.registration_id: r for r in self.registrations.get_all()}
        self.assertEqual(saved[second.registration_id].status, "confirmed")
        self.assertEqual(saved[third.registration_id].status, "waiting")

    def test_duplicate_active_registration_is_rejected(self):
        self.service.register_by_details(
            "Alex Participant", "alex@example.com", self.event
        )
        with self.assertRaises(ValueError):
            self.service.register_by_details(
                "Alex Participant", "alex@example.com", self.event
            )

    def test_concurrent_registrations_do_not_overbook(self):
        def register(index):
            service = RegistrationService(
                self.events, self.participants, self.registrations
            )
            return service.register_by_details(
                f"Person {index}", f"person{index}@example.com",
                self.events.get_by_id(self.event.event_id)
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(register, [1, 2]))

        statuses = sorted(registration.status for registration in results)
        self.assertEqual(statuses, ["confirmed", "waiting"])
        self.assertEqual(
            self.events.get_by_id(self.event.event_id).registered_count, 1
        )

    def test_event_details_persist(self):
        saved = self.events.get_by_id(self.event.event_id)
        self.assertEqual(saved.event_time, "09:30 AM")
        self.assertEqual(saved.description, "A test event")


if __name__ == "__main__":
    unittest.main()
