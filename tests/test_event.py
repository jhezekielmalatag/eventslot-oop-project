
import unittest

from models.event import Event


class TestEvent(unittest.TestCase):

    def setUp(self):
        self.event = Event(
            event_id=1,
            name="Python Seminar",
            location="Computer Laboratory",
            capacity=3
        )

    def test_initial_available_slots(self):
        self.assertEqual(self.event.available_slots, 3)

    def test_new_event_is_not_full(self):
        self.assertFalse(self.event.is_full)

    def test_available_slots_decrease(self):
        self.event.registered_count = 2
        self.assertEqual(self.event.available_slots, 1)

    def test_event_is_full(self):
        self.event.registered_count = 3
        self.assertEqual(self.event.available_slots, 0)
        self.assertTrue(self.event.is_full)

    def test_event_description(self):
        self.assertEqual(
            str(self.event),
            "Python Seminar at Computer Laboratory | "
            "Available slots: 3/3"
        )
        
    def test_occupy_slot(self):
        self.event.occupy_slot()
        self.assertEqual(self.event.registered_count, 1)


    def test_release_slot(self):
        self.event.occupy_slot()
        self.event.release_slot()
        self.assertEqual(self.event.registered_count, 0)


    def test_cannot_occupy_slot_when_full(self):
        for _ in range(self.event.capacity):
            self.event.occupy_slot()

        with self.assertRaises(ValueError):
            self.event.occupy_slot()


    def test_cannot_release_slot_when_empty(self):
        with self.assertRaises(ValueError):
            self.event.release_slot()


    def test_available_slots_after_occupying(self):
        self.event.occupy_slot()
        self.assertEqual(
            self.event.available_slots,
            self.event.capacity - 1
        )
        

if __name__ == "__main__":
    unittest.main()
