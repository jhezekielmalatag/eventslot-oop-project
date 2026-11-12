
from collections import deque
from models.registration import Registration


class RegistrationService:

    def __init__(self):
        self.registrations = []
        self.waitlists = {}
        self.next_registration_id = 1

    def _get_waitlist(self, event):
        return self.waitlists.setdefault(event.event_id, deque())

    def register_participant(self, participant, event):
        # Get this event's waitlist
        waitlist = self._get_waitlist(event)

        if event.is_full:
            # Create a waiting registration
            registration = Registration(
                self.next_registration_id,
                participant,
                event,
                "waiting"
            )

            # Add the registration to the waitlist
            waitlist.append(registration)

        else:
            # Create a confirmed registration
            registration = Registration(
                self.next_registration_id,
                participant,
                event
            )

            # Occupy an available slot
            event.occupy_slot()

        # Save the registration
        self.registrations.append(registration)

        # Prepare the next registration ID
        self.next_registration_id += 1

        return registration

    def cancel_registration(self, registration):
        if registration.status == "cancelled":
            raise ValueError("This registration is already cancelled.")

        # Get the event's waitlist
        waitlist = self._get_waitlist(registration.event)

        # Handle cancellation of waiting registrations
        if registration.status == "waiting":
            waitlist.remove(registration)
            registration.cancel()
            return

        # Release the occupied slot
        registration.event.release_slot()
        registration.cancel()

        # Promote the first participant in the waitlist
        if waitlist:
            next_registration = waitlist.popleft()
            next_registration.confirm()
            registration.event.occupy_slot()
