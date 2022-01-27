from __future__ import annotations

import unittest

import rin


class TestCache(unittest.TestCase):
    """Test :class:`.Intents`"""

    def test_default(self) -> None:
        intents = rin.Intents.default()
        self.assertEqual(intents.value, 98045)

    def test_privileged(self) -> None:
        intents = rin.Intents.privileged()
        self.assertEqual(intents.value, 258)

    def test_none(self) -> None:
        intents = rin.Intents.none()
        self.assertEqual(intents.value, 0)

    def test_create(self) -> None:
        intents = rin.Intents.create(guilds=True, guild_members=True)
        self.assertEqual(intents.value, 3)
