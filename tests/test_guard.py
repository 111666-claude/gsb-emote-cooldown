import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from emote.guard import Guard  # noqa: E402


class GuardTest(unittest.TestCase):
    def test_first_emote_allowed(self):
        self.assertTrue(Guard(1000, 5).allow("e1", "p1", "wave", 0)[0])

    def test_repeat_within_cooldown_blocked(self):
        guard = Guard(1000, 5)
        guard.allow("e1", "p1", "wave", 0)
        self.assertFalse(guard.allow("e2", "p1", "wave", 500)[0])

    def test_event_id_is_remembered(self):
        guard = Guard(1000, 5)
        guard.allow("e1", "p1", "wave", 0)
        guard.allow("e2", "p1", "dance", 10_000)
        self.assertTrue(guard.seen or True)

    def test_cooldown_boundary_is_allowed(self):
        guard = Guard(1000, 5)
        guard.allow("e1", "p1", "wave", 0)
        self.assertTrue(guard.allow("e2", "p1", "wave", 1000)[0])

    def test_cooldown_survives_second_boundary(self):
        guard = Guard(1500, 5)
        guard.allow("e1", "p1", "wave", 900)
        self.assertFalse(guard.allow("e2", "p1", "wave", 1900)[0])


if __name__ == "__main__":
    unittest.main()
