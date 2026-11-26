from models.event import Event


class AdminService:

    def __init__(self, event_repository, registration_repository):
        self.event_repository = event_repository
        self.registration_repository = registration_repository

    def create_event(self, name, location, capacity, event_time="", description=""):
        if capacity <= 0:
            raise ValueError("Event capacity must be greater than zero.")
        events = self.event_repository.get_all()
        next_event_id = max((event.event_id for event in events), default=0) + 1
        event = Event(
            next_event_id, name, location, capacity,
            event_time=event_time, description=description
        )
        self.event_repository.save(event)
        return event

    def view_all_events(self):
        return self.event_repository.get_all()

    def edit_event(
        self, event_id, name, location, capacity,
        event_time=None, description=None
    ):
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
        event.name = name.strip()
        event.location = location.strip()
        event.capacity = capacity
        if event_time is not None:
            event.event_time = event_time.strip()
        if description is not None:
            event.description = description.strip()
        self.event_repository.update(event)
        return event

    def view_all_registrations(self):
        return self.registration_repository.get_all()

    def view_event_waitlist(self, event_id):
        return [r for r in self.registration_repository.get_all()
                if r.event.event_id == event_id and r.status == "waiting"]

    def cancel_event(self, event_id):
        event = self.event_repository.get_by_id(event_id)
        if event is None:
            raise ValueError("Event not found.")
        if event.status == "cancelled":
            raise ValueError("This event is already cancelled.")
        for registration in self.registration_repository.get_all():
            if (registration.event.event_id == event_id
                    and registration.status != "cancelled"):
                registration.cancel()
                self.registration_repository.save(registration)
        event.status = "cancelled"
        self.event_repository.update(event)
        return event
