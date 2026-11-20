
from collections import deque

from models.registration import Registration


class RegistrationService:

    def __init__(
        self,
        event_repository=None,
        participant_repository=None,
        registration_repository=None
    ):
        self.registrations = []
        self.waitlists = {}
        self.next_registration_id = 1

        self.event_repository = event_repository
        self.participant_repository = participant_repository
        self.registration_repository = registration_repository

        if (
            self.event_repository
            and self.participant_repository
            and self.registration_repository
        ):
            self._load_saved_registrations()

    def _get_waitlist(self, event):
        return self.waitlists.setdefault(event.event_id, deque())

    def _load_saved_registrations(self):

        saved_registrations = self.registration_repository.get_all()

        events = {}

        for saved in saved_registrations:

            event_id = saved.event.event_id

            if event_id not in events:

                event = self.event_repository.get_by_id(event_id)

                if event is None:
                    continue

                events[event_id] = event

            event = events[event_id]

            registration = Registration(
                saved.registration_id,
                saved.participant,
                event,
                saved.status
            )

            self.registrations.append(registration)

            if registration.status == "confirmed":
                event.registered_count += 1

            elif registration.status == "waiting":
                self._get_waitlist(event).append(registration)

        if self.registrations:
            self.next_registration_id = (
                max(r.registration_id for r in self.registrations) + 1
            )

    def register_participant(self, participant, event):

        # Check whether the event already exists in the database.
        if self.event_repository:

            saved_event = self.event_repository.get_by_id(
                event.event_id
            )

            # Reject an event already cancelled in the database.
            if saved_event is not None and saved_event.status == "cancelled":
                raise ValueError(
                    "Cannot register for a cancelled event."
                )

        # Reject a cancelled event object.
        if event.status == "cancelled":
            raise ValueError(
                "Cannot register for a cancelled event."
            )

        # Save the event and participant.
        if self.event_repository and self.participant_repository:
            self.event_repository.save(event)
            self.participant_repository.save(participant)

        waitlist = self._get_waitlist(event)

        if event.is_full:

            registration = Registration(
                self.next_registration_id,
                participant,
                event,
                "waiting"
            )

            waitlist.append(registration)

        else:

            registration = Registration(
                self.next_registration_id,
                participant,
                event
            )

            event.occupy_slot()

        self.registrations.append(registration)

        if self.registration_repository:
            self.registration_repository.save(registration)

        self.next_registration_id += 1

        return registration

    def cancel_registration(self, registration):

        if registration.status == "cancelled":
            raise ValueError(
                "This registration is already cancelled."
            )

        waitlist = self._get_waitlist(registration.event)

        # Cancel a waiting registration.
        if registration.status == "waiting":

            waitlist.remove(registration)
            registration.cancel()

            if self.registration_repository:
                self.registration_repository.save(registration)

            return

        # Cancel a confirmed registration.
        registration.event.release_slot()
        registration.cancel()

        if self.registration_repository:
            self.registration_repository.save(registration)

        # Promote the first participant in the waitlist.
        if waitlist:

            next_registration = waitlist.popleft()
            next_registration.confirm()

            registration.event.occupy_slot()

            if self.registration_repository:
                self.registration_repository.save(next_registration)
