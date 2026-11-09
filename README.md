
# EventSlot — Event Registration System

## Project Overview

EventSlot is a Python-based event registration application
that manages event capacity, participant registration,
and waitlists.

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

The project will demonstrate encapsulation, abstraction,
inheritance, and polymorphism.

The Repository Pattern will separate business logic
from data storage.

## Project Status

Day 1 — Initial project setup.

## Project Status

| Day | Task | Status |
|---|---|---|
| Day 1 | Project Setup and Environment Configuration | Completed |
| Day 2 | Event Class Implementation and Unit Testing | Completed |
| Day 3 | Participant Class and Input Validation | Completed |
| Day 4 | Registration Class and Unit Testing | Completed |
| Day 5 | Event Registration Logic | Upcoming |

### Current Progress

Completed Day 4 of the EventSlot project.

The following OOP model classes have been implemented:
- **Event** – Manages event information and capacity.
- **Participant** – Stores participant information and validates input.
- **Registration** – Connects participants to events and handles registration cancellation.

**Testing:** All 15 unit tests are passing using Python's `unittest` framework.

