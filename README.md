# EventSlot — Event Registration System

## Project Overview

EventSlot is a Python-based event registration application that manages event capacity, participant registration, and waitlists.

## Objectives

- Create and manage events.
- Register participants while respecting event capacity.
- Prevent duplicate registrations.
- Add participants to a FIFO waitlist when an event is full.
- Promote the next eligible participant when a slot becomes available.
- Store event and registration information.

## Technologies

- Python
- Object-Oriented Programming (OOP)
- Streamlit
- SQLite
- unittest
- Git and GitHub

## OOP Concepts

The project demonstrates encapsulation, abstraction, inheritance, and polymorphism.

The Repository Pattern separates business logic from data storage.

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
| Day 9 | Admin Role, Event Management, and Streamlit Frontend Development | In Progress |
| Day 10 | Frontend and Backend Connection | Upcoming |
| Day 11 | Integration, Testing, and Documentation | Upcoming |
| Day 12 | Finalization and GitHub Submission | Upcoming |

## Current Progress

Completed the core registration system, SQLite database integration, and backend Admin functionality.

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
- Preventing duplicate cancellation.
- Maintaining accurate event capacity.
- Preventing registration for cancelled events.

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
- Viewing all participant registrations.
- Viewing event-specific waitlists.
- Cancelling events.
- Automatically cancelling active registrations when an event is cancelled.
- Preventing new registrations for cancelled events.

### Testing

**All 54 automated unit and integration tests successfully passed.**

Tests cover event management, participant management, registration logic, repository operations, database persistence, FIFO waitlist restoration, and Admin functionality.

## Planned Features

### Streamlit Frontend

**Status: In Progress — Day 9**

- Develop a user-friendly graphical interface using Streamlit.
- Display available events and event details.
- Allow participants to register for events.
- Display registration status and waitlist information.
- Provide an interface for Admin operations.

### Future Development

- Complete the Streamlit frontend.
- Connect the frontend to the backend services.
- Perform complete system integration and testing.
- Finalize documentation.
- Prepare the project for GitHub submission.