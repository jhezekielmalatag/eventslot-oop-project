class Registration:
    def __init__(self, registration_id, participant, event, status="confirmed"):
        self.registration_id = registration_id
        self.participant = participant
        self.event = event
        self.status = status

    def cancel(self):
        self.status = "cancelled"
        
    def confirm(self):
        self.status = "confirmed"

    def __str__(self):
        return (
            f"Registration #{self.registration_id} | "
            f"{self.participant.name} | "
            f"{self.event.name} | "
            f"Status: {self.status}"
        )