
from collections import deque
import secrets

from models.registration import Registration
from models.participant import Participant


class RegistrationService:

    def __init__(self, event_repository=None, participant_repository=None,
                 registration_repository=None):
        self.registrations = []
        self.waitlists = {}
        self.next_registration_id = 1
        self.event_repository = event_repository
        self.participant_repository = participant_repository
        self.registration_repository = registration_repository
        self.last_generated_access_code = None

        if event_repository and participant_repository and registration_repository:
            self._load_saved_registrations()

    def _get_waitlist(self, event):
        return self.waitlists.setdefault(event.event_id, deque())

    def _load_saved_registrations(self):
        self.registrations = []
        self.waitlists = {}

        saved_registrations = self.registration_repository.get_all()
        events = {}

        for saved in saved_registrations:
            event_id = saved.event.event_id

            if event_id not in events:
                event = self.event_repository.get_by_id(event_id)
                if event is None:
                    continue
                events[event_id] = event

            registration = Registration(
                saved.registration_id,
                saved.participant,
                events[event_id],
                saved.status
            )

            self.registrations.append(registration)

            if registration.status == "waiting":
                self._get_waitlist(registration.event).append(registration)

        self.next_registration_id = max(
            (r.registration_id for r in self.registrations),
            default=0
        ) + 1

    def register_by_details(self, name, email, event):
        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("Participant name cannot be empty.")

        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please provide a valid email address.")

        if self.participant_repository is None:
            raise ValueError("Participant storage is not configured.")

        self.last_generated_access_code = None

        participant, generated_code = (
            self.participant_repository.get_or_create_by_email(
                name,
                email,
                secrets.token_hex(4).upper()
            )
        )

        self.last_generated_access_code = generated_code

        return self.register_participant(participant, event)

    def register_participant(self, participant, event):
        if self.participant_repository:
            existing_participant = (
                self.participant_repository.get_by_email(participant.email)
            )

            if existing_participant is not None:
                participant.participant_id = existing_participant.participant_id

                if not participant.access_code:
                    participant.access_code = existing_participant.access_code

            if not participant.access_code:
                participant.access_code = secrets.token_hex(4).upper()
                self.last_generated_access_code = participant.access_code

        if self.event_repository:
            saved_event = self.event_repository.get_by_id(event.event_id)

            if saved_event is None:
                self.event_repository.save(event)
                saved_event = self.event_repository.get_by_id(event.event_id)

            if saved_event is None:
                raise ValueError("Unable to save or retrieve the event.")

            if saved_event.status == "cancelled":
                raise ValueError("Cannot register for a cancelled event.")

            event.registered_count = saved_event.registered_count
            event.capacity = saved_event.capacity
            event.status = saved_event.status
            event.name = saved_event.name
            event.location = saved_event.location
            event.event_time = saved_event.event_time
            event.description = saved_event.description

        if event.status == "cancelled":
            raise ValueError("Cannot register for a cancelled event.")

        existing_registrations = (
            self.registration_repository.get_all()
            if self.registration_repository
            else self.registrations
        )

        for existing in existing_registrations:
            if (
                existing.event.event_id == event.event_id
                and existing.participant.email.lower() == participant.email.lower()
                and existing.status in ("confirmed", "waiting")
            ):
                raise ValueError(
                    "You already have an active registration for this event."
                )

        if self.participant_repository:
            self.participant_repository.save(participant)

        waitlist = self._get_waitlist(event)
        registration = Registration(
            self.next_registration_id,
            participant,
            event
        )

        use_atomic = (
            self.event_repository is not None
            and self.participant_repository is not None
            and self.registration_repository is not None
            and hasattr(self.registration_repository, "create_with_capacity")
        )

        if use_atomic:
            self.registration_repository.create_with_capacity(registration)

            refreshed_event = self.event_repository.get_by_id(event.event_id)

            if refreshed_event is None:
                raise ValueError("Event not found after registration.")

            event.registered_count = refreshed_event.registered_count

        else:
            if event.is_full:
                registration.status = "waiting"
                waitlist.append(registration)
            else:
                registration.status = "confirmed"
                event.occupy_slot()

            if self.registration_repository:
                self.registration_repository.save(registration)

        if registration.status == "waiting" and registration not in waitlist:
            waitlist.append(registration)

        self.registrations.append(registration)

        self.next_registration_id = max(
            self.next_registration_id,
            registration.registration_id + 1
        )

        return registration

    def cancel_registration(self, registration):
        registration_id = registration.registration_id

        # Database-backed cancellation.
        if self.registration_repository and self.event_repository:
            self._load_saved_registrations()

            target = next(
                (
                    item for item in self.registrations
                    if item.registration_id == registration_id
                ),
                None
            )

            if target is None:
                raise ValueError("Registration not found.")

            event = self.event_repository.get_by_id(
                target.event.event_id
            )

            if event is None:
                raise ValueError("Event not found.")

            target.event = event

        else:
            # In-memory cancellation.
            target = next(
                (
                    item for item in self.registrations
                    if item.registration_id == registration_id
                ),
                registration
            )

            event = target.event

        if target.status == "cancelled":
            raise ValueError("This registration is already cancelled.")

        waitlist = self._get_waitlist(event)

        # Cancel a waiting registration without releasing a slot.
        if target.status == "waiting":
            self.waitlists[event.event_id] = type(waitlist)(
                item for item in waitlist
                if item.registration_id != registration_id
            )

            target.cancel()

            if self.registration_repository:
                self.registration_repository.save(target)

            return

        if target.status != "confirmed":
            raise ValueError("Invalid registration status.")

        # Release the occupied slot.
        event.release_slot()
        target.cancel()

        if self.registration_repository:
            self.registration_repository.save(target)

        # Promote the first participant in the FIFO waitlist.
        if waitlist:
            next_registration = waitlist.popleft()
            next_registration.confirm()

            if self.registration_repository:
                self.registration_repository.save(next_registration)
            else:
                event.occupy_slot()

    def view_all_registrations(self):
        return (
            self.registration_repository.get_all()
            if self.registration_repository
            else list(self.registrations)
        )

    def view_event_waitlist(self, event_id):
        return [
            r for r in self.view_all_registrations()
            if r.event.event_id == event_id and r.status == "waiting"
        ]

    def view_participant_registrations(self, participant_id):
        if self.registration_repository:
            return self.registration_repository.get_by_participant_id(
                participant_id
            )

        return [
            r for r in self.registrations
            if r.participant.participant_id == participant_id
        ]
