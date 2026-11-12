
class Event:
    def __init__(self, event_id, name, location, capacity):
        self.event_id = event_id
        self.name = name
        self.location = location
        self.capacity = capacity
        self.registered_count = 0

    @property
    def available_slots(self):
        return self.capacity - self.registered_count

    @property
    def is_full(self):
        return self.available_slots == 0
    
    def occupy_slot(self):
        if self.is_full:
            raise ValueError("No available slots for this event.")

        self.registered_count += 1


    def release_slot(self):
        if self.registered_count <= 0:
            raise ValueError("There are no occupied slots to release.")

        self.registered_count -= 1

    def __str__(self):
        return (
            f"{self.name} at {self.location} | "
            f"Available slots: {self.available_slots}/{self.capacity}"
        )
