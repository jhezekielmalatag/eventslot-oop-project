from models.registration import Registration


class RegistrationService:

    def __init__(self):
        self.registrations = []
        self.next_registration_id = 1

    def register_participant(self, participant, event):
        # Check if the event is already full
        if event.is_full:
            raise ValueError("This event is already full.")

        # Create a new registration
        registration = Registration(
            self.next_registration_id,
            participant,
            event
        )

        # Update the event's registered count
        event.registered_count += 1

        # Save the registration
        self.registrations.append(registration)

        # Prepare the next registration ID
        self.next_registration_id += 1

        return registration