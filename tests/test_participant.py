import unittest
from models.participant import Participant


class TestParticipant(unittest.TestCase):

    def test_valid_participant(self):
        participant = Participant(1, "Juan Dela Cruz", "juan@example.com")
        self.assertEqual(participant.name, "Juan Dela Cruz")
        self.assertEqual(participant.email, "juan@example.com")

    def test_name_is_trimmed(self):
        participant = Participant(1, "  Juan Dela Cruz  ", "juan@example.com")
        self.assertEqual(participant.name, "Juan Dela Cruz")

    def test_empty_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Participant(1, "   ", "juan@example.com")

    def test_invalid_email_is_rejected(self):
        with self.assertRaises(ValueError):
            Participant(1, "Juan Dela Cruz", "invalid-email")

    def test_participant_description(self):
        participant = Participant(1, "Juan Dela Cruz", "juan@example.com")
        self.assertEqual(
            str(participant),
            "Juan Dela Cruz (juan@example.com)"
        )


if __name__ == "__main__":
    unittest.main()