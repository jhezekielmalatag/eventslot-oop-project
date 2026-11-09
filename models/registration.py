class Registration:
    def __init__(self, registration_id, participant, event):
        self.registration_id = registration_id
        self.participant = participant
        self.event = event
        self.status = "confirmed"

    def cancel(self):
        self.status = "cancelled"

    def __str__(self):
        return (
            f"Registration #{self.registration_id} | "
            f"{self.participant.name} | "
            f"{self.event.name} | "
            f"Status: {self.status}"
        )