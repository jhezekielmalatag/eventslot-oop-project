class EventRequest:

    WAITING = "Waiting for Approval"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

    def __init__(
        self,
        request_id,
        applicant_name,
        email,
        organization,
        event_name,
        location,
        event_time,
        purpose,
        status=WAITING,
        admin_feedback="",
        tracking_code=""
    ):
        self.request_id = request_id
        self.applicant_name = applicant_name
        self.email = email
        self.organization = organization
        self.event_name = event_name
        self.location = location
        self.event_time = event_time
        self.purpose = purpose
        self.status = status
        self.admin_feedback = admin_feedback
        self.tracking_code = tracking_code

    def accept(self, feedback=""):
        self.status = self.ACCEPTED
        self.admin_feedback = feedback

    def reject(self, feedback=""):
        self.status = self.REJECTED
        self.admin_feedback = feedback

    def __str__(self):
        return (
            f"{self.event_name} | "
            f"Applicant: {self.applicant_name} | "
            f"Status: {self.status}"
        )