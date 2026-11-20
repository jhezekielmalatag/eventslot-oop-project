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

The project will demonstrate encapsulation, abstraction, inheritance, and polymorphism.

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
| Day 9 | Admin Role and Event Management | Upcoming |
| Day 10 | Streamlit Frontend Development | Upcoming |
| Day 11 | Frontend and Backend Connection | Upcoming |
| Days 12–14 | Integration, Testing, Documentation, and Finalization | Upcoming |

## Current Progress

Completed Day 8 of the EventSlot project.

### RegistrationService

The `RegistrationService` handles participant registration, cancellation, event slot management, and FIFO waitlist processing. It is now integrated with SQLite repositories for persistent data storage.

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

### Testing

**All 46 automated unit and integration tests successfully passed.**

Tests cover event management, participant management, registration logic, repository operations, database persistence, and FIFO waitlist restoration.

## Planned Features

### Admin Management

**Status: Planned — Not Yet Implemented**

- Create, edit, and view events.
- View participant registrations.
- Monitor event waitlists.
- Cancel events.

The Admin feature will be developed after completing the core registration and FIFO waitlist functionality and before Streamlit frontend development.

### Future Development

- Admin role and event management.
- Streamlit-based graphical user interface.
- Frontend and backend integration.
- Complete system integration and testing.
- Final documentation and GitHub submission.