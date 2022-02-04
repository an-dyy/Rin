from __future__ import annotations

import rin


class TestIntents:
    def test_default(self) -> None:
        intents = rin.Intents.default()
        assert intents.value == 98045

    def test_privileged(self) -> None:
        intents = rin.Intents.privileged()
        assert intents.value == 258

    def test_none(self) -> None:
        intents = rin.Intents.none()
        assert intents.value == 0

    def test_create(self) -> None:
        intents = rin.Intents.create(guilds=True, guild_members=True)
        assert intents.value == 3
