
from repositories.database import Database
from repositories.event_reposity import EventRepository
from models.event import Event


def main():
    db = Database()
    db.create_tables()

    event_repository = EventRepository(db)

    # Retrieve an existing event
    event = event_repository.get_by_id(2)

    if event is None:
        print("Event not found.")
        return

    # Update the event details
    event.name = "Updated OOP Project Presentation"
    event.location = "Computer Laboratory"
    event.capacity = 60

    # Save the changes using update()
    result = event_repository.update(event)

    if result:
        print("Event successfully updated!")
    else:
        print("Event update failed.")

    # Display the updated event
    updated_event = event_repository.get_by_id(2)
    print(updated_event)


if __name__ == "__main__":
    main()
