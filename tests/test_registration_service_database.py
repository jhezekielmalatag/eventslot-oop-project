
import os
import unittest

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.participant_repository import ParticipantRepository
from repositories.registration_repository import RegistrationRepository

from services.registration_service import RegistrationService
from models.event import Event
from models.participant import Participant


class TestRegistrationServiceDatabase(unittest.TestCase):

    def setUp(self):
        self.database_name = "test_eventslot_integration.db"

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.database = Database(self.database_name)
        self.database.create_tables()

        self.event_repository = EventRepository(self.database)
        self.participant_repository = ParticipantRepository(self.database)
        self.registration_repository = RegistrationRepository(self.database)

        self.event = Event(
            1,
            "Python Workshop",
            "Library",
            1
        )

        self.service = RegistrationService(
            self.event_repository,
            self.participant_repository,
            self.registration_repository
        )

    def tearDown(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def create_participant(self, participant_id, name):
        return Participant(
            participant_id,
            name,
            f"participant{participant_id}@example.com"
        )

    def create_service(self):
        return RegistrationService(
            self.event_repository,
            self.participant_repository,
            self.registration_repository
        )

    def test_restore_registrations_after_restart(self):
        first = self.create_participant(1, "Juan")
        second = self.create_participant(2, "Maria")

        self.service.register_participant(first, self.event)
        self.service.register_participant(second, self.event)

        # Simulate restarting the service.
        restarted_service = self.create_service()

        self.assertEqual(len(restarted_service.registrations), 2)

        self.assertEqual(
            restarted_service.registrations[0].status,
            "confirmed"
        )

        self.assertEqual(
            restarted_service.registrations[1].status,
            "waiting"
        )

        restored_event = restarted_service.registrations[0].event

        self.assertEqual(restored_event.registered_count, 1)

    def test_fifo_waitlist_after_restart(self):
        first = self.create_participant(1, "Juan")
        second = self.create_participant(2, "Maria")
        third = self.create_participant(3, "Pedro")

        self.service.register_participant(first, self.event)
        self.service.register_participant(second, self.event)
        self.service.register_participant(third, self.event)

        # Restart the service.
        restarted_service = self.create_service()

        # Cancel the first confirmed registration.
        first_registration = restarted_service.registrations[0]
        restarted_service.cancel_registration(first_registration)

        # Retrieve the saved registrations.
        saved_second = self.registration_repository.get_by_id(2)
        saved_third = self.registration_repository.get_by_id(3)

        # Maria must be promoted before Pedro.
        self.assertEqual(saved_second.status, "confirmed")
        self.assertEqual(saved_third.status, "waiting")

    def test_registration_id_continues_after_restart(self):
        first = self.create_participant(1, "Juan")

        self.service.register_participant(first, self.event)

        restarted_service = self.create_service()

        second = self.create_participant(2, "Maria")

        registration = restarted_service.register_participant(
            second,
            self.event
        )

        self.assertEqual(registration.registration_id, 2)


if __name__ == "__main__":
    unittest.main()
