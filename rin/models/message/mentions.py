from __future__ import annotations

from typing import Any

import attr

__all__ = ("AllowedMentions",)


@attr.s(kw_only=True)
class AllowedMentions:
    everyone: bool = attr.field(default=True)
    roles: bool | list[int] = attr.field(default=True)
    users: bool | list[int] = attr.field(default=True)
    replied_user: bool = attr.field(default=True)

    @classmethod
    def none(cls: type[AllowedMentions]) -> AllowedMentions:
        return cls(everyone=False, roles=False, users=False, replied_user=False)

    def to_dict(self) -> dict[Any, Any]:
        payload: dict[str, list[str] | bool] = {
            "everyone": self.everyone,
            "replied_user": self.replied_user,
        }

        parse: list[str] = []

        if self.roles is True:
            parse.append("roles")

            if isinstance(self.roles, list):
                payload["roles"] = self.roles

        if self.users is True:
            parse.append("users")

            if isinstance(self.users, list):
                payload["users"] = self.users

        payload["parse"] = parse
        return payload
