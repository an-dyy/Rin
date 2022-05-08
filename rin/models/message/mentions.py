from __future__ import annotations

import attr

__all__ = ("AllowedMentions",)


@attr.s(kw_only=True)
class AllowedMentions:
    """Represents an allowed mentions object.

    This is used to determine the allowed mentions of any messages being sent from the client's user.

    Parameters
    ----------
    everyone: :class:`bool`
        If mentioning everyone is allowed. By default True.

    roles: :class:`bool` | :class:`list`
        Either a list of role IDs, or a boolean value. Determines the allowed roles to be mentioned.

    users: :class:`bool` | :class:`list`
        Either a list of user IDs, or a boolean value. Dtermines the allowed users to be mentioned.

    replied_user: :class:`bool`
        If mentioning the replied user to the message is allowed.
    """

    everyone: bool = attr.field(default=True)
    roles: bool | list[int] = attr.field(default=True)
    users: bool | list[int] = attr.field(default=True)
    replied_user: bool = attr.field(default=True)

    @classmethod
    def none(cls: type[AllowedMentions]) -> AllowedMentions:
        """Creates a :class:`.AllowedMentions` instance that has no
        allowed mentions set.

        Returns
        -------
        :class:`.AllowedMentions`
            The created instance.
        """
        return cls(everyone=False, roles=False, users=False, replied_user=False)

    def to_dict(self) -> dict[str, bool | list[int] | list[str]]:
        """Turns the AllowedMentions instance into a usable dict.

        Returns
        -------
        :class:`dict`
            The created dict from the AllowedMentions instance.
        """
        payload: dict[str, bool | list[int] | list[str]] = {
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
