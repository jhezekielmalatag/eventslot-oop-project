
from models.event import Event


def main():
    event = Event(
        event_id=1,
        name="Python Programming Seminar",
        location="Computer Laboratory",
        capacity=3
    )

    print("=== EventSlot: Event Tests ===")
    print(event)

    # Test 1: A new event has all its slots available.
    assert event.available_slots == 3
    assert event.is_full is False
    print("Test 1 passed: Initial capacity")

    # Test 2: Simulate two participants registering.
    event.registered_count = 2
    assert event.available_slots == 1
    assert event.is_full is False
    print("Test 2 passed: Remaining slots")

    # Test 3: Simulate the event becoming full.
    event.registered_count = 3
    assert event.available_slots == 0
    assert event.is_full is True
    print("Test 3 passed: Full event")

    print("\nAll manual tests passed!")


if __name__ == "__main__":
    main()
