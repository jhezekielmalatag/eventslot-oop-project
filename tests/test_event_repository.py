
import os
import unittest

from repositories.database import Database
from repositories.event_repository import EventRepository
from models.event import Event


class TestEventRepository(unittest.TestCase):

    def setUp(self):
        self.database_name = "test_eventslot.db"

        if os.path.exists(self.database_name):
            os.remove(self.database_name)

        self.database = Database(self.database_name)
        self.database.create_tables()

        self.event_repository = EventRepository(self.database)

        self.event = Event(
            event_id=1,
            name="Python Workshop",
            location="Library",
            capacity=30
        )

    def tearDown(self):
        if os.path.exists(self.database_name):
            os.remove(self.database_name)

    def test_save_event(self):
        self.event_repository.save(self.event)

        saved_event = self.event_repository.get_by_id(1)

        self.assertIsNotNone(saved_event)
        self.assertEqual(saved_event.name, "Python Workshop")

    def test_get_by_id(self):
        self.event_repository.save(self.event)

        saved_event = self.event_repository.get_by_id(1)

        self.assertEqual(saved_event.event_id, 1)

    def test_get_by_id_returns_none_when_missing(self):
        result = self.event_repository.get_by_id(999)

        self.assertIsNone(result)

    def test_get_all(self):
        self.event_repository.save(self.event)

        second_event = Event(
            event_id=2,
            name="OOP Seminar",
            location="Computer Laboratory",
            capacity=50
        )

        self.event_repository.save(second_event)

        events = self.event_repository.get_all()

        self.assertEqual(len(events), 2)

    def test_update_event(self):
        self.event_repository.save(self.event)

        self.event.name = "Updated Python Workshop"
        self.event.capacity = 60

        result = self.event_repository.update(self.event)

        updated_event = self.event_repository.get_by_id(1)

        self.assertTrue(result)
        self.assertEqual(updated_event.name, "Updated Python Workshop")
        self.assertEqual(updated_event.capacity, 60)

    def test_update_returns_false_when_event_missing(self):
        missing_event = Event(
            event_id=999,
            name="Missing Event",
            location="Library",
            capacity=20
        )

        result = self.event_repository.update(missing_event)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
