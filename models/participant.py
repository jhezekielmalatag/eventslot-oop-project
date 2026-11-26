class Participant:
    def __init__(self, participant_id, name, email, access_code=None):
        name = name.strip()
        email = email.strip().lower()

        if not name:
            raise ValueError("Participant name cannot be empty.")

        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please provide a valid email address.")

        self.participant_id = participant_id
        self.name = name
        self.email = email
        self.access_code = access_code

    def __str__(self):
        return f"{self.name} ({self.email})"
