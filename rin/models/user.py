from __future__ import annotations

import base64

import attr
import magic

from ..rest import Route
from .base import BaseModel
from .cacheable import Cacheable
from .snowflake import Snowflake


@attr.s(slots=True)
class User(BaseModel, Cacheable):
    """Represents a discord user.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the user.

    discriminator: :class:`str`
        The user's discriminator.

    username: :class:`str`
        The username of the user.

    avatar: None | :class:`str`
        The avatar hash of the user.

    banner: None | :class:`str`
        The banner hash of the user.

    accent_color: None | :class:`int`
        The accent color of the user.

    bot :class:`bool`
        If the user is a bot user.

    system: :class:`bool`
        If the user is an offical discord system user.

    mfa_enabled: :class:`bool`
        If the user has mfa enabled.

    verified: :class:`bool`
        If the user's email is verified. Given with the email scope.

    email: None | :class:`str`
        The user's email which is connected to the account. Given with the email scope.

    locale: None | :class:`str`
        The language option of the user. Given with the identify scope.

    flags: :class:`int`
        The flags of the user's account. Given with the identify scope.

    public_flags: :class:`int`
        The public flags on the user's accoumt. Given with the identify scope.

    premium: :class:`int`
        The premium type of the user. Given with the identify scope.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake)
    discriminator: str = BaseModel.field(None, str)
    username: str = BaseModel.field(None, str)

    avatar: None | str = BaseModel.field(None, str)
    banner: None | str = BaseModel.field(None, str)
    accent_color: None | int = BaseModel.field(None, int)

    bot: bool = BaseModel.field(None, bool, default=False)
    system: bool = BaseModel.field(None, bool, default=False)
    mfa_enabled: bool = BaseModel.field(None, bool, default=False)
    verified: bool = BaseModel.field(None, bool, default=False)

    email: None | str = BaseModel.field(None, str)
    locale: None | str = BaseModel.field(None, str)

    flags: int = BaseModel.field(None, int, default=0)
    public_flags: int = BaseModel.field(None, int, default=0)
    premium: int = BaseModel.field("premium_type", int, default=0)

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        User.cache.set(self.snowflake, self)

    async def edit(
        self, username: str | None = None, avatar: None | bytes = None
    ) -> User:
        """Edits the current authorized user.

        Parameters
        ----------
        username: None | :class:`str`
            The new username to give the user.

        avatar: None | :class:`bytes`
            The new avatar to give the user.

        Raises
        ------
        :exc:`HTTPException`
            Something went wrong.

        Returns
        -------
        :class:`.User`
            The user after editting is finished.
        """
        if self.client.user is self:
            payload = {}

            if username is not None:
                payload["username"] = username

            if avatar is not None:
                mime = magic.from_buffer(avatar, mime=True)
                payload[
                    "avatar"
                ] = f"data:{mime};base64,{base64.b64encode(avatar).decode('ascii')}"

            self.data = await self.client.rest.request(
                "PATCH", Route("users/@me"), json=payload
            )

            self.username = username if username is not None else self.username
            self.avatar = self.data.get("avatar") or self.avatar

        return self
