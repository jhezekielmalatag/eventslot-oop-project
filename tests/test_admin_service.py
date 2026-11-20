
import unittest
import os

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.participant_repository import ParticipantRepository
from repositories.registration_repository import RegistrationRepository

from services.admin_service import AdminService
from services.registration_service import RegistrationService

from models.participant import Participant


class TestAdminService(unittest.TestCase):

    def setUp(self):

        self.database = Database("test_admin.db")
        self.database.create_tables()

        self.event_repository = EventRepository(self.database)
        self.participant_repository = ParticipantRepository(self.database)
        self.registration_repository = RegistrationRepository(self.database)

        self.admin_service = AdminService(
            self.event_repository,
            self.registration_repository
        )

        self.registration_service = RegistrationService(
            self.event_repository,
            self.participant_repository,
            self.registration_repository
        )

    def tearDown(self):

        if os.path.exists("test_admin.db"):
            os.remove("test_admin.db")

    def test_create_event(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            50
        )

        self.assertEqual(event.event_id, 1)
        self.assertEqual(event.name, "Python Seminar")
        self.assertEqual(event.status, "active")

    def test_view_all_events(self):

        self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            50
        )

        events = self.admin_service.view_all_events()

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "Python Seminar")

    def test_edit_event(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            50
        )

        updated_event = self.admin_service.edit_event(
            event.event_id,
            "Advanced Python Seminar",
            "Computer Laboratory",
            60
        )

        saved_event = self.event_repository.get_by_id(event.event_id)

        self.assertEqual(updated_event.name, "Advanced Python Seminar")
        self.assertEqual(saved_event.location, "Computer Laboratory")
        self.assertEqual(saved_event.capacity, 60)

    def test_cannot_reduce_capacity_below_confirmed_registrations(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            5
        )

        participant = Participant(
            1,
            "Juan Dela Cruz",
            "juan@example.com"
        )

        self.registration_service.register_participant(
            participant,
            event
        )

        with self.assertRaises(ValueError):
            self.admin_service.edit_event(
                event.event_id,
                "Python Seminar",
                "School Auditorium",
                0
            )

    def test_view_all_registrations(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            2
        )

        participant = Participant(
            1,
            "Juan Dela Cruz",
            "juan@example.com"
        )

        self.registration_service.register_participant(
            participant,
            event
        )

        registrations = self.admin_service.view_all_registrations()

        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0].participant.name, "Juan Dela Cruz")

    def test_view_event_waitlist(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            1
        )

        first = Participant(1, "Juan", "juan@example.com")
        second = Participant(2, "Maria", "maria@example.com")

        self.registration_service.register_participant(first, event)
        self.registration_service.register_participant(second, event)

        waitlist = self.admin_service.view_event_waitlist(event.event_id)

        self.assertEqual(len(waitlist), 1)
        self.assertEqual(waitlist[0].participant.name, "Maria")

    def test_cancel_event(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            2
        )

        participant = Participant(
            1,
            "Juan",
            "juan@example.com"
        )

        self.registration_service.register_participant(
            participant,
            event
        )

        cancelled_event = self.admin_service.cancel_event(event.event_id)

        saved_event = self.event_repository.get_by_id(event.event_id)
        registrations = self.admin_service.view_all_registrations()

        self.assertEqual(cancelled_event.status, "cancelled")
        self.assertEqual(saved_event.status, "cancelled")
        self.assertEqual(registrations[0].status, "cancelled")

    def test_cannot_register_for_cancelled_event(self):

        event = self.admin_service.create_event(
            "Python Seminar",
            "School Auditorium",
            2
        )

        self.admin_service.cancel_event(event.event_id)

        participant = Participant(
            1,
            "Juan",
            "juan@example.com"
        )

        with self.assertRaises(ValueError):
            self.registration_service.register_participant(
                participant,
                event
            )


if __name__ == "__main__":
    unittest.main()
