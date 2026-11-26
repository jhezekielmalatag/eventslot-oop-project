
import os
import streamlit as st
from pathlib import Path
from html import escape

from repositories.database import Database
from repositories.event_repository import EventRepository
from repositories.registration_repository import RegistrationRepository
from repositories.participant_repository import ParticipantRepository
from repositories.event_request_repository import EventRequestRepository

from services.admin_service import AdminService
from services.event_request_service import EventRequestService
from services.registration_service import RegistrationService


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="EventSlot | Event Management",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================
# HTML RENDERING
# =========================================

def render_html(content, container=None):
    if container is None:
        container = st

    container.html(content)


# =========================================
# LOAD CUSTOM CSS
# =========================================

def load_css():

    css_file = Path(__file__).resolve().parent / "style.css"

    if not css_file.is_file():
        st.error(f"CSS file not found: {css_file}")
        return

    try:
        css_content = css_file.read_text(encoding="utf-8")

        st.html(f"""
            <style>
            {css_content}
            </style>
        """)

    except OSError as error:
        st.error(f"Could not load CSS: {error}")


# =========================================
# DATABASE AND SERVICES
# =========================================

@st.cache_resource
def get_services():

    database = Database()
    database.create_tables()

    event_repository = EventRepository(database)
    registration_repository = RegistrationRepository(database)
    participant_repository = ParticipantRepository(database)
    event_request_repository = EventRequestRepository(database)

    admin_service = AdminService(
        event_repository,
        registration_repository
    )

    event_request_service = EventRequestService(
        event_request_repository,
        admin_service
    )

    registration_service = RegistrationService(
        event_repository,
        participant_repository,
        registration_repository
    )

    return (
        event_repository,
        registration_repository,
        admin_service,
        event_request_service,
        participant_repository,
        registration_service
    )


# =========================================
# ADMIN PASSWORD
# =========================================

def get_admin_password():

    password = os.environ.get("EVENTSLOT_ADMIN_PASSWORD")

    if password:
        return password

    try:
        return st.secrets["admin"]["password"]
    except (KeyError, FileNotFoundError):
        return None


# =========================================
# REUSABLE UI COMPONENTS
# =========================================

def stat_card(label, value, description):

    render_html(f"""
        <div class="stat-card">
            <div class="stat-label">{escape(str(label))}</div>
            <div class="stat-value">{escape(str(value))}</div>
            <div class="stat-description">
                {escape(str(description))}
            </div>
        </div>
    """)


def section_heading(title, subtitle):

    render_html(f"""
        <div class="section-header">
            <h2>{escape(str(title))}</h2>
            <p>{escape(str(subtitle))}</p>
        </div>
    """)


def page_heading(eyebrow, title, description):

    render_html(f"""
        <div class="page-heading">
            <div class="eyebrow">{escape(str(eyebrow))}</div>
            <h1>{escape(str(title))}</h1>
            <p>{escape(str(description))}</p>
        </div>
    """)


def event_card(event):

    name = escape(str(event.name))
    location = escape(str(event.location))

    if str(event.status).lower() == "active":
        badge_class = "active-badge"
        badge_text = "Active"
    else:
        badge_class = "cancelled-badge"
        badge_text = "Cancelled"

    render_html(f"""
        <div class="event-card">
            <div class="event-card-top">
                <span class="status-badge {badge_class}">
                    {badge_text}
                </span>
            </div>

            <h3>{name}</h3>

            <div class="event-detail">
                <span class="detail-label">Location</span>
                <span class="detail-value">{location}</span>
            </div>

            <div class="event-detail">
                <span class="detail-label">Capacity</span>
                <span class="detail-value">
                    {event.capacity} participants
                </span>
            </div>
        </div>
    """)


def request_status_display(request):

    if request.status == "Waiting for Approval":
        st.warning("Waiting for Approval")
        st.write(
            "Your request has been received and is waiting "
            "for administrator review."
        )

    elif request.status == "Accepted":
        st.success("Accepted")
        st.write(
            "Your event request has been approved and "
            "your event has been added to EventSlot."
        )

    elif request.status == "Rejected":
        st.error("Rejected")
        st.write(
            "Unfortunately, your event request was not approved."
        )

    if request.admin_feedback:
        st.markdown("**Administrator Feedback**")
        st.info(request.admin_feedback)


# =========================================
# APPLICANT REQUEST STATUS CARD
# =========================================

def public_request_card(request):

    if request.status == "Waiting for Approval":
        status_class = "waiting"
        description = (
            "Your proposal has been received and is waiting "
            "for administrator review."
        )

    elif request.status == "Accepted":
        status_class = "accepted"
        description = (
            "Your proposal has been approved. Your event "
            "has been added to the EventSlot Events page."
        )

    else:
        status_class = "rejected"
        description = (
            "Your proposal was not approved. Please review "
            "the administrator feedback below."
        )

    applicant_name = escape(str(request.applicant_name))
    event_name = escape(str(request.event_name))
    location = escape(str(request.location))
    event_time = escape(str(request.event_time))
    event_description = escape(str(request.purpose))
    status = escape(str(request.status))
    description = escape(description)

    feedback_html = ""

    if request.admin_feedback:
        feedback_html = f"""
            <div class="request-feedback">
                <div class="request-field-label">
                    Administrator Feedback
                </div>
                <div class="request-field-value">
                    {escape(str(request.admin_feedback))}
                </div>
            </div>
        """

    render_html(f"""
        <div class="request-status-board {status_class}">

            <div class="request-board-top">
                <div>
                    <div class="request-field-label">
                        APPLICANT
                    </div>
                    <h2>{applicant_name}</h2>
                </div>

                <div class="request-status-badge">
                    {status}
                </div>
            </div>

            <div class="request-board-description">
                {description}
            </div>

            <div class="request-board-details">

                <div class="request-field">
                    <div class="request-field-label">
                        Event Title
                    </div>
                    <div class="request-field-value">
                        {event_name}
                    </div>
                </div>

                <div class="request-field">
                    <div class="request-field-label">
                        Proposed Location
                    </div>
                    <div class="request-field-value">
                        {location}
                    </div>
                </div>

                <div class="request-field">
                    <div class="request-field-label">
                        Event Time
                    </div>
                    <div class="request-field-value">
                        {event_time}
                    </div>
                </div>

                <div class="request-field">
                    <div class="request-field-label">
                        Event Description
                    </div>
                    <div class="request-field-value">
                        {event_description}
                    </div>
                </div>

            </div>

            {feedback_html}

        </div>
    """)


# =========================================
# HOME PAGE
# =========================================

def home_page(event_repository, registration_repository):

    events = event_repository.get_all()
    registrations = registration_repository.get_all()

    active_events = [
        event for event in events
        if event.status == "active"
    ]

    confirmed = [
        registration for registration in registrations
        if registration.status == "confirmed"
    ]

    waiting = [
        registration for registration in registrations
        if registration.status == "waiting"
    ]

    render_html("""
        <div class="hero">
            <div class="eyebrow">
                EVENT MANAGEMENT PLATFORM
            </div>

            <h1>
                Manage events.<br>
                Bring people together.
            </h1>

            <p>
                Discover events, organize your own activities,
                and bring your community together through EventSlot.
            </p>
        </div>
    """)

    section_heading(
        "Dashboard Overview",
        "A quick overview of events and registrations."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stat_card("Total Events", len(events), "All created events")

    with col2:
        stat_card("Active Events", len(active_events), "Currently available")

    with col3:
        stat_card(
            "Confirmed Registrations",
            len(confirmed),
            "Successfully registered"
        )

    with col4:
        stat_card(
            "Waiting List",
            len(waiting),
            "Awaiting available slots"
        )

    section_heading(
        "Recent Events",
        "Explore the latest active events."
    )

    if not active_events:
        st.info("No active events are available yet.")

    else:
        recent_events = active_events[-3:][::-1]
        columns = st.columns(3)

        for index, event in enumerate(recent_events):
            with columns[index]:
                event_card(event)

    with st.expander("Administrative Access"):

        st.caption(
            "Restricted area. Authorized administrators only."
        )

        if st.session_state.get("admin_authenticated", False):

            st.success("Administrator session is active.")

            if st.button(
                "Open Admin Dashboard",
                key="open_admin_dashboard"
            ):
                st.session_state.page = "Admin Dashboard"
                st.rerun()

        else:

            with st.form("admin_login_form"):

                password = st.text_input(
                    "Administrator Password",
                    type="password"
                )

                login_submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True
                )

                if login_submitted:

                    correct_password = get_admin_password()

                    if correct_password is None:
                        st.error(
                            "Admin password has not been configured."
                        )

                    elif password == correct_password:
                        st.session_state.admin_authenticated = True
                        st.session_state.page = "Admin Dashboard"
                        st.rerun()

                    else:
                        st.error("Incorrect administrator password.")


# =========================================
# MY EVENTS SECTION
# =========================================

def my_events_section(
    participant_repository,
    registration_repository,
    registration_service
):

    with st.container(key="my_events_section"):

        # DISPLAY CANCELLATION SUCCESS AFTER RERUN
        if st.session_state.pop("cancellation_success", False):
            st.success(
                "Your registration has been cancelled successfully!"
            )

        section_heading(
            "My Events",
            "Retrieve your registrations using your email address and private access code."
        )

        # ACCESS CODE LOOKUP FORM
        with st.form("my_events_lookup_form"):

            lookup_email = st.text_input(
                "Email Address",
                placeholder="The email used when registering"
            )

            lookup_code = st.text_input(
                "Private Access Code",
                placeholder="Enter your 8-character access code",
                type="password"
            )

            lookup_submitted = st.form_submit_button(
                "View My Events",
                use_container_width=True
            )

        # VERIFY PARTICIPANT
        if lookup_submitted:

            if not lookup_email.strip() or not lookup_code.strip():
                st.warning(
                    "Enter both your email address and access code."
                )

                st.session_state.pop(
                    "my_events_verified_email", None
                )
                st.session_state.pop(
                    "my_events_verified_code", None
                )
                st.session_state.pop(
                    "pending_cancellation_id", None
                )
                return

            participant = (
                participant_repository.get_by_email_and_access_code(
                    lookup_email.strip(),
                    lookup_code.strip().upper()
                )
            )

            if participant is None:
                st.error(
                    "We couldn't verify those details. "
                    "Check your email and access code."
                )

                st.session_state.pop(
                    "my_events_verified_email", None
                )
                st.session_state.pop(
                    "my_events_verified_code", None
                )
                st.session_state.pop(
                    "pending_cancellation_id", None
                )
                return

            st.session_state.my_events_verified_email = (
                lookup_email.strip()
            )

            st.session_state.my_events_verified_code = (
                lookup_code.strip().upper()
            )

            st.session_state.pop(
                "pending_cancellation_id", None
            )

        # RESTORE VERIFIED PARTICIPANT AFTER RERUN
        verified_email = st.session_state.get(
            "my_events_verified_email"
        )

        verified_code = st.session_state.get(
            "my_events_verified_code"
        )

        if not verified_email or not verified_code:
            st.caption(
                "Your access code was shown after your first "
                "successful registration. Keep it private."
            )
            return

        participant = (
            participant_repository.get_by_email_and_access_code(
                verified_email,
                verified_code
            )
        )

        if participant is None:
            st.error(
                "Your session could not be verified. "
                "Please enter your email and access code again."
            )

            st.session_state.pop(
                "my_events_verified_email", None
            )
            st.session_state.pop(
                "my_events_verified_code", None
            )
            st.session_state.pop(
                "pending_cancellation_id", None
            )
            return

        # LOAD REGISTRATIONS
        registrations = (
            registration_repository.get_by_participant_id(
                participant.participant_id
            )
        )

        section_heading(
            f"Welcome, {participant.name}",
            "Your latest registration records are shown below."
        )

        if not registrations:
            st.info("You don't have any event registrations yet.")
            return

        # DISPLAY REGISTRATION CARDS
        for registration in registrations:

            event = registration.event
            status = registration.status.lower()
            registration_id = registration.registration_id

            with st.container(border=True):

                st.subheader(event.name)

                if status == "confirmed":
                    st.success(
                        "Confirmed — your place is reserved."
                    )

                elif status == "waiting":
                    st.warning(
                        "Waitlisted — you'll be promoted "
                        "when a place becomes available."
                    )

                elif status == "cancelled":
                    st.error("Cancelled")

                else:
                    st.info(status.title())

                st.write(f"**Location:** {event.location}")

                st.write(
                    f"**Time:** "
                    f"{event.event_time or 'Not specified'}"
                )

                st.write(
                    f"**Description:** "
                    f"{event.description or 'No description provided.'}"
                )

                # PARTICIPANT CANCELLATION
                if status in ("confirmed", "waiting"):

                    pending_id = st.session_state.get(
                        "pending_cancellation_id"
                    )

                    if pending_id == registration_id:

                        st.warning(
                            "Are you sure you want to cancel this registration?"
                        )

                        confirm_col, keep_col = st.columns(2)

                        # CONFIRM CANCELLATION
                        with confirm_col:

                            if st.button(
                                "Yes, Cancel Registration",
                                key=f"confirm_cancel_{registration_id}",
                                type="primary",
                                use_container_width=True
                            ):

                                try:
                                    registration_service.cancel_registration(
                                        registration
                                    )

                                    st.session_state.pop(
                                        "pending_cancellation_id",
                                        None
                                    )

                                    # SAVE SUCCESS MESSAGE BEFORE RERUN
                                    st.session_state["cancellation_success"] = True

                                    st.rerun()

                                except ValueError as error:
                                    st.error(str(error))

                        # KEEP REGISTRATION
                        with keep_col:

                            if st.button(
                                "Keep Registration",
                                key=f"keep_registration_{registration_id}",
                                use_container_width=True
                            ):

                                st.session_state.pop(
                                    "pending_cancellation_id",
                                    None
                                )

                                st.rerun()

                    else:

                        # INITIAL CANCELLATION BUTTON
                        if st.button(
                            "Cancel Reservation",
                            key=f"cancel_reservation_{registration_id}",
                            use_container_width=True
                        ):

                            st.session_state.pending_cancellation_id = (
                                registration_id
                            )

                            st.rerun()


# =========================================
# AVAILABLE EVENTS PAGE
# =========================================

def available_events_page(
    event_repository,
    registration_repository,
    registration_service,
    participant_repository
):

    page_heading(
        "EVENTS",
        "Available Events",
        "Explore events, view their details, reserve your place, and track your registrations."
    )

    selected_event_id = st.session_state.get("selected_event_id")

    if selected_event_id is not None:

        selected_event = event_repository.get_by_id(selected_event_id)

        if selected_event is None or selected_event.status != "active":
            st.session_state.pop("selected_event_id", None)
            selected_event = None

        if selected_event is not None:

            if st.button("← Back to Events", key="back_to_events"):
                st.session_state.pop("selected_event_id", None)
                st.rerun()

            show_event_details(
                selected_event,
                event_repository,
                registration_repository,
                registration_service
            )

            return

    my_events_tab, browse_tab = st.tabs([
        "My Events",
        "Browse Events"
    ])

    with my_events_tab:

        my_events_section(
            participant_repository,
            registration_repository,
            registration_service
        )

    with browse_tab:

        events = event_repository.get_all()

        active_events = [
            event for event in events
            if event.status == "active"
        ]

        if not active_events:
            st.info("No active events are available yet.")

        else:

            columns = st.columns(2)

            for index, event in enumerate(active_events):

                with columns[index % 2]:

                    event_card(event)

                    if st.button(
                        "View Event Details",
                        key=f"view_event_{event.event_id}",
                        use_container_width=True
                    ):

                        st.session_state.selected_event_id = event.event_id
                        st.rerun()


# =========================================
# EVENT DETAILS AND REGISTRATION
# =========================================

def show_event_details(
    event,
    event_repository,
    registration_repository,
    registration_service
):

    # Refresh event information from the database.
    event = event_repository.get_by_id(event.event_id)

    if event is None:
        st.error("This event could not be found.")
        st.session_state.pop("selected_event_id", None)
        return

    if event.status != "active":
        st.error("This event is no longer available for registration.")
        return

    registrations = registration_repository.get_by_event(event.event_id)

    waiting_count = sum(
        1 for registration in registrations
        if registration.status == "waiting"
    )

    section_heading(
        event.name,
        "Event information and registration"
    )

    st.write(f"**Location:** {event.location}")
    st.write(f"**Time:** {event.event_time or 'Not specified'}")

    st.write(
        f"**Description:** "
        f"{event.description or 'No description provided.'}"
    )

    available = max(
        event.capacity - event.registered_count,
        0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        stat_card(
            "Capacity",
            event.capacity,
            "Total available places"
        )

    with col2:
        stat_card(
            "Remaining Slots",
            available,
            "Confirmed places still open"
        )

    with col3:
        stat_card(
            "Waiting List",
            waiting_count,
            "Participants waiting"
        )

    # REGISTRATION RESULT
    if st.session_state.get("registration_result_event") == event.event_id:

        result = st.session_state.get("registration_result")

        if result == "confirmed":
            st.success(
                "Registration confirmed! Your place is reserved."
            )

        elif result == "waiting":
            st.warning(
                "The event is full. You have been added "
                "to the FIFO waiting list."
            )

        access_code = st.session_state.pop(
            "generated_access_code",
            None
        )

        if access_code:
            st.success(
                "Your private My Events access code has been generated."
            )

            st.code(access_code)

            st.warning(
                "Save this code somewhere safe. You will need it "
                "together with your email address to view your registrations."
            )

        st.session_state.pop("registration_result", None)
        st.session_state.pop("registration_result_event", None)

    # REGISTRATION FORM
    section_heading(
        "Join This Event",
        "Enter your details to register for this event."
    )

    with st.form(
        f"join_event_form_{event.event_id}",
        clear_on_submit=True
    ):

        participant_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        participant_email = st.text_input(
            "Email Address",
            placeholder="example@email.com"
        )

        submitted = st.form_submit_button(
            "Join Event",
            use_container_width=True
        )

        if submitted:

            try:

                latest_event = event_repository.get_by_id(event.event_id)

                if latest_event is None or latest_event.status != "active":
                    st.error("This event is no longer available.")
                    return

                registration = registration_service.register_by_details(
                    participant_name,
                    participant_email,
                    latest_event
                )

                st.session_state.registration_result = registration.status

                st.session_state.registration_result_event = (
                    event.event_id
                )

                generated_code = (
                    registration_service.last_generated_access_code
                )

                if generated_code:
                    st.session_state.generated_access_code = generated_code
                    registration_service.last_generated_access_code = None

                st.rerun()

            except ValueError as error:
                st.error(str(error))


# =========================================
# CREATE EVENT PAGE
# =========================================

def create_request_page(event_request_service):

    page_heading(
        "EVENT SUBMISSION",
        "Create an Event",
        "Submit your event proposal and follow its approval status."
    )

    # APPLICANT REQUEST STATUS
    applicant_email = st.session_state.get("applicant_email")

    if applicant_email:

        requests = event_request_service.event_request_repository.get_by_email(
            applicant_email
        )

        section_heading(
            "Your Event Requests",
            "View the latest status of your submitted proposals."
        )

        if requests:
            for request in requests:
                public_request_card(request)

        else:
            st.info("You have not submitted any event requests yet.")

        if st.button(
            "Refresh Request Status",
            use_container_width=True,
            key="refresh_request_status"
        ):
            st.rerun()

        st.divider()

    else:

        section_heading(
            "Your Event Requests",
            "Your submitted proposals will appear here automatically."
        )

        st.info(
            "After submitting your first event proposal, "
            "its status will appear here automatically."
        )

        st.divider()

    # NEW EVENT REQUEST FORM
    section_heading(
        "Submit a New Event",
        "Tell us about yourself and the event you want to organize."
    )

    st.info(
        "Your proposal will be reviewed by an administrator. "
        "It will only appear on the public Events page after approval."
    )

    with st.form("event_request_form", clear_on_submit=True):

        st.markdown("**Applicant Information**")

        applicant_name = st.text_input(
            "Full Name",
            value=st.session_state.get("applicant_name", ""),
            placeholder="Enter your full name"
        )

        email = st.text_input(
            "Email Address",
            value=st.session_state.get("applicant_email", ""),
            placeholder="example@email.com"
        )

        organization = st.text_input(
            "Organization",
            placeholder="Enter your organization"
        )

        st.write("")
        st.markdown("**Event Information**")

        event_name = st.text_input(
            "Event Title",
            placeholder="Enter your event title"
        )

        location = st.text_input(
            "Event Location",
            placeholder="Enter the proposed venue"
        )

        st.markdown("**Event Time (12-hour format)**")

        time_col1, time_col2, time_col3 = st.columns(3)

        with time_col1:
            event_hour = st.selectbox(
                "Hour",
                [f"{hour:02d}" for hour in range(1, 13)],
                index=8
            )

        with time_col2:
            event_minute = st.selectbox(
                "Minute",
                [f"{minute:02d}" for minute in range(60)],
                index=0
            )

        with time_col3:
            event_period = st.selectbox(
                "AM / PM",
                ["AM", "PM"],
                index=0
            )

        event_time = f"{event_hour}:{event_minute} {event_period}"

        purpose = st.text_area(
            "Event Description",
            placeholder="Describe your event, its activities, and objectives.",
            height=150
        )

        submitted = st.form_submit_button(
            "Submit Event Request",
            use_container_width=True
        )

        if submitted:

            try:

                request = event_request_service.submit_request(
                    applicant_name=applicant_name,
                    email=email,
                    organization=organization,
                    event_name=event_name,
                    location=location,
                    event_time=event_time,
                    purpose=purpose
                )

                st.session_state.applicant_name = request.applicant_name
                st.session_state.applicant_email = request.email

                st.success(
                    "Your event request has been submitted successfully."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))


# =========================================
# ADMIN REQUEST REVIEW
# =========================================

def admin_request_review(event_request_service):

    requests = event_request_service.view_all_requests()

    pending_requests = [
        request for request in requests
        if request.status == "Waiting for Approval"
    ]

    accepted_requests = [
        request for request in requests
        if request.status == "Accepted"
    ]

    rejected_requests = [
        request for request in requests
        if request.status == "Rejected"
    ]

    section_heading(
        "Event Request Overview",
        "Review submissions and manage applicant decisions."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        stat_card(
            "Waiting for Approval",
            len(pending_requests),
            "Requests awaiting review"
        )

    with col2:
        stat_card(
            "Accepted",
            len(accepted_requests),
            "Approved submissions"
        )

    with col3:
        stat_card(
            "Rejected",
            len(rejected_requests),
            "Declined submissions"
        )

    section_heading(
        "Pending Submissions",
        "Review each proposal before making a decision."
    )

    if not pending_requests:
        st.success("There are no pending event requests.")

    else:

        request_options = {
            f"EVT-{request.request_id:06d} | {request.event_name}":
            request.request_id
            for request in pending_requests
        }

        selected_label = st.selectbox(
            "Select an Event Request",
            list(request_options.keys())
        )

        selected_id = request_options[selected_label]

        request = event_request_service.view_request(selected_id)

        with st.container(border=True):

            st.subheader(request.event_name)

            request_status_display(request)

            st.write(f"**Applicant:** {request.applicant_name}")
            st.write(f"**Email:** {request.email}")
            st.write(f"**Organization:** {request.organization}")
            st.write(f"**Event Location:** {request.location}")
            st.write(f"**Event Time:** {request.event_time}")

            st.markdown("**Event Description**")
            st.write(request.purpose)

        approve_column, reject_column = st.columns(2)

        with approve_column:

            section_heading(
                "Accept Request",
                "Approve the proposal and publish the event."
            )

            with st.form(f"approve_request_{request.request_id}"):

                capacity = st.number_input(
                    "Event Capacity",
                    min_value=1,
                    value=50,
                    step=1
                )

                approval_feedback = st.text_area(
                    "Approval Message (Optional)"
                )

                approve_submitted = st.form_submit_button(
                    "Accept Event Request",
                    use_container_width=True
                )

                if approve_submitted:

                    try:

                        event = event_request_service.approve_request(
                            request.request_id,
                            capacity,
                            approval_feedback
                        )

                        st.success(
                            f"Request accepted. "
                            f"'{event.name}' is now an active event."
                        )

                        st.rerun()

                    except ValueError as error:
                        st.error(str(error))

        with reject_column:

            section_heading(
                "Reject Request",
                "Decline the proposal and provide a reason."
            )

            with st.form(f"reject_request_{request.request_id}"):

                rejection_feedback = st.text_area(
                    "Reason for Rejection"
                )

                reject_submitted = st.form_submit_button(
                    "Reject Event Request",
                    use_container_width=True
                )

                if reject_submitted:

                    try:

                        event_request_service.reject_request(
                            request.request_id,
                            rejection_feedback
                        )

                        st.success(
                            "The event request has been rejected."
                        )

                        st.rerun()

                    except ValueError as error:
                        st.error(str(error))

    # REVIEWED REQUESTS
    section_heading(
        "Reviewed Requests",
        "Previously accepted and rejected submissions."
    )

    reviewed_requests = [
        request for request in requests
        if request.status != "Waiting for Approval"
    ]

    if not reviewed_requests:
        st.info("No requests have been reviewed yet.")

    else:

        for request in reversed(reviewed_requests):

            with st.expander(
                f"EVT-{request.request_id:06d} | "
                f"{request.event_name} | {request.status}"
            ):

                st.write(f"**Applicant:** {request.applicant_name}")
                st.write(f"**Email:** {request.email}")
                st.write(f"**Organization:** {request.organization}")
                st.write(f"**Event Location:** {request.location}")
                st.write(f"**Event Time:** {request.event_time}")

                st.markdown("**Event Description**")
                st.write(request.purpose)

                request_status_display(request)


# =========================================
# ADMIN EVENT MANAGEMENT
# =========================================

def admin_event_management(admin_service):

    section_heading(
        "Manage Published Events",
        "View, edit, and cancel events already published in EventSlot."
    )

    events = admin_service.view_all_events()

    if not events:
        st.info("No events have been created yet.")
        return

    for event in events:

        with st.expander(
            f"{event.name} | {event.status.title()} | {event.event_id}"
        ):

            st.write(f"**Location:** {event.location}")
            st.write(f"**Time:** {event.event_time or 'Not specified'}")
            st.write(f"**Description:** {event.description or 'No description'}")

            st.write(
                f"**Confirmed:** {event.registered_count}/{event.capacity} | "
                f"**Remaining:** "
                f"{max(event.capacity - event.registered_count, 0)}"
            )

            if event.status == "active":

                with st.form(f"edit_event_{event.event_id}"):

                    st.markdown("**Edit Event Details**")

                    edited_name = st.text_input(
                        "Event Name",
                        value=event.name,
                        key=f"edit_name_{event.event_id}"
                    )

                    edited_location = st.text_input(
                        "Location",
                        value=event.location,
                        key=f"edit_location_{event.event_id}"
                    )

                    edited_capacity = st.number_input(
                        "Capacity",
                        min_value=1,
                        value=int(event.capacity),
                        step=1,
                        key=f"edit_capacity_{event.event_id}"
                    )

                    edited_time = st.text_input(
                        "Event Time",
                        value=event.event_time,
                        key=f"edit_time_{event.event_id}"
                    )

                    edited_description = st.text_area(
                        "Description",
                        value=event.description,
                        key=f"edit_description_{event.event_id}"
                    )

                    edit_submitted = st.form_submit_button(
                        "Save Event Changes",
                        use_container_width=True
                    )

                    if edit_submitted:

                        try:

                            admin_service.edit_event(
                                event.event_id,
                                edited_name,
                                edited_location,
                                int(edited_capacity),
                                edited_time,
                                edited_description
                            )

                            st.success("Event details updated.")
                            st.rerun()

                        except ValueError as error:
                            st.error(str(error))

                if st.button(
                    "Cancel Event",
                    key=f"cancel_event_{event.event_id}"
                ):

                    try:

                        admin_service.cancel_event(event.event_id)

                        st.success(
                            "Event cancelled and active registrations cancelled."
                        )

                        st.rerun()

                    except ValueError as error:
                        st.error(str(error))

            event_registrations = [
                registration
                for registration in admin_service.view_all_registrations()
                if registration.event.event_id == event.event_id
            ]

            confirmed = [
                registration for registration in event_registrations
                if registration.status == "confirmed"
            ]

            waiting = [
                registration for registration in event_registrations
                if registration.status == "waiting"
            ]

            st.markdown("**Confirmed Registrations**")

            if confirmed:

                for registration in confirmed:

                    st.write(
                        f"#{registration.registration_id} — "
                        f"{registration.participant.name} "
                        f"({registration.participant.email})"
                    )

            else:
                st.caption("No confirmed registrations yet.")

            st.markdown("**FIFO Waiting List**")

            if waiting:

                for position, registration in enumerate(waiting, start=1):

                    st.write(
                        f"{position}. {registration.participant.name} "
                        f"({registration.participant.email})"
                    )

            else:
                st.caption("No participants on the waiting list.")


# =========================================
# ADMIN REGISTRATION OVERVIEW
# =========================================

def admin_registration_overview(admin_service):

    section_heading(
        "Registration Management",
        "Review confirmed participants and waiting-list entries across all events."
    )

    registrations = admin_service.view_all_registrations()

    if not registrations:
        st.info("There are no registrations yet.")
        return

    confirmed = [
        registration for registration in registrations
        if registration.status == "confirmed"
    ]

    waiting = [
        registration for registration in registrations
        if registration.status == "waiting"
    ]

    cancelled = [
        registration for registration in registrations
        if registration.status == "cancelled"
    ]

    c1, c2, c3 = st.columns(3)

    with c1:
        stat_card("Confirmed", len(confirmed), "Reserved places")

    with c2:
        stat_card("Waiting", len(waiting), "FIFO queue entries")

    with c3:
        stat_card("Cancelled", len(cancelled), "Cancelled registrations")

    for registration in registrations:

        st.write(
            f"**{registration.event.name}** — "
            f"{registration.participant.name} "
            f"({registration.participant.email}) — "
            f"{registration.status.title()}"
        )


# =========================================
# ADMIN DASHBOARD
# =========================================

def admin_dashboard(admin_service, event_request_service):

    if not st.session_state.get("admin_authenticated", False):

        st.session_state.page = "Home"
        st.error("Administrator authentication is required.")
        st.rerun()
        return

    page_heading(
        "ADMINISTRATION",
        "Admin Dashboard",
        "Manage event submissions and published events."
    )

    col1, col2 = st.columns([5, 1])

    with col1:
        st.caption("Private EventSlot Management Workspace")

    with col2:

        if st.button("Log Out", use_container_width=True):

            st.session_state.admin_authenticated = False
            st.session_state.page = "Home"
            st.rerun()

    st.divider()

    admin_tab, events_tab, registrations_tab = st.tabs([
        "Event Requests",
        "Published Events",
        "Registrations"
    ])

    with admin_tab:
        admin_request_review(event_request_service)

    with events_tab:
        admin_event_management(admin_service)

    with registrations_tab:
        admin_registration_overview(admin_service)


# =========================================
# SIDEBAR NAVIGATION
# =========================================

def sidebar_navigation():

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    render_html("""
        <div class="sidebar-brand">
            <div class="brand-name">EventSlot</div>
            <div class="brand-subtitle">
                EVENT MANAGEMENT SYSTEM
            </div>
        </div>

        <div class="nav-heading">WORKSPACE</div>
    """, st.sidebar)

    pages = [
        "Home",
        "Events",
        "Create"
    ]

    if st.session_state.page not in pages + ["Admin Dashboard"]:
        st.session_state.page = "Home"

    for page_name in pages:

        selected = st.session_state.page == page_name

        if st.sidebar.button(
            page_name,
            key=f"nav_{page_name.lower()}",
            type="primary" if selected else "secondary",
            use_container_width=True
        ):

            st.session_state.page = page_name
            st.rerun()

    render_html("""
        <div class="sidebar-footer">
            <div class="footer-title">EventSlot</div>
            <div>Version 1.0</div>
            <div>Event Management Workspace</div>
        </div>
    """, st.sidebar)

    return st.session_state.page


# =========================================
# MAIN APPLICATION
# =========================================

def main():

    load_css()

    (
        event_repository,
        registration_repository,
        admin_service,
        event_request_service,
        participant_repository,
        registration_service
    ) = get_services()

    menu = sidebar_navigation()

    if menu == "Home":

        home_page(
            event_repository,
            registration_repository
        )

    elif menu == "Events":

        available_events_page(
            event_repository,
            registration_repository,
            registration_service,
            participant_repository
        )

    elif menu == "Create":

        create_request_page(event_request_service)

    elif menu == "Admin Dashboard":

        admin_dashboard(
            admin_service,
            event_request_service
        )

    render_html("""
        <div class="app-footer">
            EventSlot — Event Registration System
            <span>Built with Python, SQLite and Streamlit</span>
        </div>
    """)


if __name__ == "__main__":
    main()
