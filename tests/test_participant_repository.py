
import os
import unittest

from repositories.database import Database
from repositories.participant_repository import ParticipantRepository
from models.participant import Participant


class TestParticipantRepository(unittest.TestCase):

    def setUp(self):
        self.database_name = "test_eventslot.db"

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.database = Database(self.database_name)
        self.database.create_tables()

        self.participant_repository = ParticipantRepository(self.database)

        self.participant = Participant(
            participant_id=1,
            name="Juan Dela Cruz",
            email="juan@example.com"
        )

    def tearDown(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def test_save_participant(self):
        self.participant_repository.save(self.participant)

        saved_participant = self.participant_repository.get_by_id(1)

        self.assertIsNotNone(saved_participant)
        self.assertEqual(saved_participant.name, "Juan Dela Cruz")

    def test_get_by_id(self):
        self.participant_repository.save(self.participant)

        saved_participant = self.participant_repository.get_by_id(1)

        self.assertEqual(saved_participant.email, "juan@example.com")

    def test_get_by_id_returns_none_when_missing(self):
        result = self.participant_repository.get_by_id(999)

        self.assertIsNone(result)

    def test_get_all(self):
        self.participant_repository.save(self.participant)

        second_participant = Participant(
            participant_id=2,
            name="Maria Santos",
            email="maria@example.com"
        )

        self.participant_repository.save(second_participant)

        participants = self.participant_repository.get_all()

        self.assertEqual(len(participants), 2)


if __name__ == "__main__":
    unittest.main()
