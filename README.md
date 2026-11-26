# EventSlot — Event Registration System

## Project Overview

EventSlot is a Python-based event registration application that manages event capacity, participant registration, and FIFO waitlists. It provides a Streamlit interface for participants and administrators to interact with the system.

## Objectives

- Create and manage events.
- Register participants while respecting event capacity.
- Prevent duplicate registrations.
- Add participants to a FIFO waitlist when an event is full.
- Promote the next eligible participant when a slot becomes available.
- Store event and registration information using SQLite.
- Provide an interface for participants and administrators to manage event activities.

## Technologies

- Python
- Object-Oriented Programming (OOP)
- Streamlit
- SQLite
- unittest
- Git and GitHub

## OOP Concepts

The project demonstrates the following Object-Oriented Programming concepts:

- **Encapsulation** — Organizing data and related operations within classes.
- **Abstraction** — Hiding implementation details and exposing necessary operations.
- **Inheritance** — Reusing and extending class functionality where applicable.
- **Polymorphism** — Supporting different implementations of common operations where applicable.

The Repository Pattern separates business logic from data storage, improving modularity and maintainability.

## Project Status

| Day | Task | Status |
|---|---|---|
| Day 1 | Project Setup and Environment Configuration | Completed |
| Day 2 | Event Class Implementation and Unit Testing | Completed |
| Day 3 | Participant Class and Input Validation | Completed |
| Day 4 | Registration Class and Unit Testing | Completed |
| Day 5 | Event Registration Logic | Completed |
| Day 6 | Slot Management | Completed |
| Day 7 | FIFO Waitlist Implementation | Completed |
| Day 8 | SQLite Database, Repository Implementation, Backend Integration, and Testing | Completed |
| Day 9 | Admin Role and Event Management | Completed |
| Day 10 | Streamlit Frontend Development and Backend Connection | Completed |
| Day 11 | Integration Testing and Documentation | In Progress |
| Day 12 | Finalization and GitHub Submission | In Progress |

## Current Progress

The core registration system, SQLite database integration, backend Admin functionality, and Streamlit frontend have been implemented.

### RegistrationService

The `RegistrationService` handles participant registration, cancellation, event slot management, and FIFO waitlist processing. It is integrated with SQLite repositories for persistent data storage.

### Implemented Features

- Registering participants for available event slots.
- Adding participants to a waitlist when an event is full.
- Managing separate waitlists for individual events.
- Using Python's `deque` to implement FIFO queue behavior.
- Automatically promoting the first waiting participant when a confirmed registration is cancelled.
- Removing cancelled waiting participants from the waitlist.
- Releasing occupied slots after registration cancellation.
- Preventing duplicate registrations and cancellations.
- Maintaining accurate event capacity.
- Preventing registration for cancelled events.
- Handling concurrent registration attempts to prevent overbooking.

### SQLite Database Integration

- Created SQLite database connection and table management.
- Implemented the `events`, `participants`, and `registrations` tables.
- Implemented `EventRepository`.
- Implemented `ParticipantRepository`.
- Implemented `RegistrationRepository`.
- Connected `RegistrationService` to the repositories.
- Added persistent registration and cancellation records.
- Restored registrations, occupied event slots, and FIFO waitlists after service restart.
- Maintained registration ID sequencing after restart.
- Added event status persistence and database migration support.

### Admin Management

The `AdminService` provides administrative operations for managing events and monitoring registrations.

Implemented features:

- Creating new events.
- Viewing all events.
- Editing event details.
- Preventing invalid event capacity updates.
- Viewing participant registrations.
- Viewing event-specific waitlists.
- Cancelling events.
- Automatically cancelling active registrations when an event is cancelled.
- Preventing new registrations for cancelled events.

### Streamlit Frontend

The Streamlit frontend connects the application's user interface to its backend services.

Implemented features:

- Browsing published events and viewing event details.
- Registering participants through the interface.
- Displaying registration results and statuses.
- Providing a My Events section for participants.
- Retrieving personal registrations using an email address and private access code.
- Providing administrative event management.
- Displaying participant registrations and waitlists.
- Supporting event cancellation and management through the Admin interface.
- Applying a customized interface with a dark visual theme.

### Testing

**All 71 automated unit and integration tests successfully passed in the latest confirmed test run.**

Tests cover event management, participant management, registration logic, repository operations, database persistence, FIFO waitlist restoration, Admin functionality, and concurrent registration handling.

## Planned Features and Improvements

### Documentation and Finalization

**Status: In Progress — Day 11–12**

- Review and finalize project documentation.
- Verify the README and repository contents.
- Perform final application checks.
- Prepare the project for submission.

### Future Development

- Deploy the application online using Render.
- Configure persistent database storage for online use.
- Continue improving application security and usability.

## Author

**John Hezekiel Malatag**  
BS Computer Science — 2nd Year