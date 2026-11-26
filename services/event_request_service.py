import secrets

from models.event_request import EventRequest


class EventRequestService:

    def __init__(self, event_request_repository, admin_service):
        self.event_request_repository = event_request_repository
        self.admin_service = admin_service

    def submit_request(
        self, applicant_name, email, organization, event_name,
        location, event_time, purpose
    ):
        if not all([
            applicant_name.strip(), email.strip(), organization.strip(),
            event_name.strip(), location.strip(), event_time.strip(), purpose.strip()
        ]):
            raise ValueError("All fields are required.")

        email = email.strip().lower()
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Please enter a valid email address.")

        requests = self.event_request_repository.get_all()
        next_request_id = max(
            (request.request_id for request in requests), default=0
        ) + 1
        tracking_code = secrets.token_hex(8).upper()
        event_request = EventRequest(
            request_id=next_request_id,
            applicant_name=applicant_name.strip(),
            email=email,
            organization=organization.strip(),
            event_name=event_name.strip(),
            location=location.strip(),
            event_time=event_time.strip(),
            purpose=purpose.strip(),
            tracking_code=tracking_code
        )
        self.event_request_repository.save(event_request)
        return event_request

    def view_all_requests(self):
        return self.event_request_repository.get_all()

    def view_request(self, request_id):
        request = self.event_request_repository.get_by_id(request_id)
        if request is None:
            raise ValueError("Event request not found.")
        return request

    def check_request_status(self, request_id, tracking_code):
        request = self.event_request_repository.get_by_tracking_details(
            request_id, tracking_code.strip().upper()
        )
        if request is None:
            raise ValueError("No matching event request was found.")
        return request

    def approve_request(self, request_id, capacity, feedback=""):
        request = self.view_request(request_id)
        if request.status != EventRequest.WAITING:
            raise ValueError("This request has already been reviewed.")
        try:
            capacity = int(capacity)
        except (ValueError, TypeError):
            raise ValueError("Event capacity must be a valid number.")
        if capacity <= 0:
            raise ValueError("Event capacity must be greater than zero.")

        event = self.admin_service.create_event(
            request.event_name,
            request.location,
            capacity,
            event_time=request.event_time,
            description=request.purpose
        )
        request.accept(feedback.strip())
        self.event_request_repository.update(request)
        return event

    def reject_request(self, request_id, feedback=""):
        request = self.view_request(request_id)
        if request.status != EventRequest.WAITING:
            raise ValueError("This request has already been reviewed.")
        if not feedback.strip():
            raise ValueError("Please provide a reason for rejection.")
        request.reject(feedback.strip())
        self.event_request_repository.update(request)
        return request
