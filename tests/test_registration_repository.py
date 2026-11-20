
import os
import unittest

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.participant_repository import ParticipantRepository
from repositories.registration_repository import RegistrationRepository

from models.event import Event
from models.participant import Participant
from models.registration import Registration


class TestRegistrationRepository(unittest.TestCase):

    def setUp(self):
        self.database_name = "test_eventslot.db"

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.database = Database(self.database_name)
        self.database.create_tables()

        self.event_repository = EventRepository(self.database)
        self.participant_repository = ParticipantRepository(self.database)
        self.registration_repository = RegistrationRepository(self.database)

        self.event = Event(1, "Python Workshop", "Library", 30)
        self.participant = Participant(
            1, "Juan Dela Cruz", "juan@example.com"
        )

        self.event_repository.save(self.event)
        self.participant_repository.save(self.participant)

        self.registration = Registration(
            1, self.participant, self.event
        )

    def tearDown(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def test_save_registration(self):
        self.registration_repository.save(self.registration)

        saved = self.registration_repository.get_by_id(1)

        self.assertIsNotNone(saved)
        self.assertEqual(saved.status, "confirmed")

    def test_get_by_id(self):
        self.registration_repository.save(self.registration)

        saved = self.registration_repository.get_by_id(1)

        self.assertEqual(saved.participant.name, "Juan Dela Cruz")
        self.assertEqual(saved.event.name, "Python Workshop")

    def test_get_by_id_returns_none_when_missing(self):
        result = self.registration_repository.get_by_id(999)

        self.assertIsNone(result)

    def test_get_all(self):
        self.registration_repository.save(self.registration)

        second_participant = Participant(
            2, "Maria Santos", "maria@example.com"
        )
        self.participant_repository.save(second_participant)

        second_registration = Registration(
            2, second_participant, self.event, "waiting"
        )
        self.registration_repository.save(second_registration)

        registrations = self.registration_repository.get_all()

        self.assertEqual(len(registrations), 2)
        self.assertEqual(registrations[0].status, "confirmed")
        self.assertEqual(registrations[1].status, "waiting")


if __name__ == "__main__":
    unittest.main()
