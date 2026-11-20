
from models.event import Event


class AdminService:

    def __init__(
        self,
        event_repository,
        registration_repository
    ):
        self.event_repository = event_repository
        self.registration_repository = registration_repository

    def create_event(self, name, location, capacity):

        if capacity <= 0:
            raise ValueError("Event capacity must be greater than zero.")

        events = self.event_repository.get_all()

        next_event_id = max(
            (event.event_id for event in events),
            default=0
        ) + 1

        event = Event(
            next_event_id,
            name,
            location,
            capacity
        )

        self.event_repository.save(event)

        return event

    def view_all_events(self):

        return self.event_repository.get_all()

    def edit_event(self, event_id, name, location, capacity):

        event = self.event_repository.get_by_id(event_id)

        if event is None:
            raise ValueError("Event not found.")

        if event.status == "cancelled":
            raise ValueError("Cannot edit a cancelled event.")

        if capacity <= 0:
            raise ValueError("Event capacity must be greater than zero.")

        if capacity < event.registered_count:
            raise ValueError(
                "Capacity cannot be lower than the number of confirmed registrations."
            )

        event.name = name
        event.location = location
        event.capacity = capacity

        self.event_repository.update(event)

        return event

    def view_all_registrations(self):

        return self.registration_repository.get_all()

    def view_event_waitlist(self, event_id):

        registrations = self.registration_repository.get_all()

        waitlist = [
            registration
            for registration in registrations
            if registration.event.event_id == event_id
            and registration.status == "waiting"
        ]

        return waitlist

    def cancel_event(self, event_id):

        event = self.event_repository.get_by_id(event_id)

        if event is None:
            raise ValueError("Event not found.")

        if event.status == "cancelled":
            raise ValueError("This event is already cancelled.")

        registrations = self.registration_repository.get_all()

        for registration in registrations:

            if (
                registration.event.event_id == event_id
                and registration.status != "cancelled"
            ):
                registration.cancel()
                self.registration_repository.save(registration)

        event.status = "cancelled"
        event.registered_count = 0

        self.event_repository.update(event)

        return event
