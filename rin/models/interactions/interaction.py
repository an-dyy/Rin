from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..assets import File
from ..base import BaseModel
from ..builders import EmbedBuilder
from ..message import ActionRow, AllowedMentions, Message, Modal
from ..snowflake import Snowflake
from ..user import User
from .types import InteractionResponse, InteractionType

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("Interaction",)


@attr.s(slots=True)
class Interaction(BaseModel):
    """Represents an interaction.

    Attributes
    ----------
    snowflake: :class:`.Snowflake`
        The snowflake of the interaction.

    application_id: :class:`.Snowflake`
        The interaction's application snowflake.

    actual_data: :class:`dict`
        A dictionary of the raw data of the interaction.

    guild_id: None | :class:`.Snowflake`
        The snowflake of the guild where the interaction is in.

    channel_id: None | :class:`.Snowflake`
        The snowflake of the channel where the interaction is in.

    member: None | :class:`dict`
        The member which caused the interaction.

    user: None | :class:`.User`
        The user which caused the interaction.

    token: :class:`str`
        The token of the interaction.

    version: :class:`int`
       The version of the interaction. Always set to ``1``.

    message: None | :class:`.Message`
        The message of the interaction. Only given when interaction was
        fired from a component.

    locale: None | :class:`str`
        The locale of the invoking user.

    guild_locale: None | :class:`str`
        The locale of the guild where the interaction was invoked.
    """

    snowflake: Snowflake = BaseModel.field("id", Snowflake)
    application_id: Snowflake = BaseModel.field(None, Snowflake)
    actual_data: dict[Any, Any] = BaseModel.field("data", dict)

    guild_id: None | Snowflake = BaseModel.field(None, Snowflake)
    channel_id: None | Snowflake = BaseModel.field(None, Snowflake)

    member: None | dict[Any, Any] = BaseModel.field(None, dict)
    user: None | User = BaseModel.field(None, User)

    token: str = BaseModel.field(None, str)
    version: int = BaseModel.field(None, int)
    message: Message = BaseModel.field(None, Message)

    locale: None | str = BaseModel.field(None, str)
    guild_locale: None | str = BaseModel.field(None, str)

    @BaseModel.property("type", InteractionType)
    def type(self, _: GatewayClient, data: int) -> InteractionType:
        return InteractionType(data)

    async def modal(self, modal: Modal) -> None:
        inter = {"type": InteractionResponse.MODAL, "data": modal.to_dict()}
        await self.client.rest.request(
            "POST",
            Route(f"interactions/{self.snowflake}/{self.token}/callback"),
            json=inter,
        )

    async def send(
        self,
        content: None | str = None,
        tts: bool = False,
        embeds: list[EmbedBuilder] = [],
        files: list[File] = [],
        rows: list[ActionRow] = [],
        reply: None | Message = None,
        ephemeral: bool = False,
        mentions: AllowedMentions = AllowedMentions(),
    ) -> Message:
        """Sends a message to respond to an interaction.

        Parameters
        ----------
        content: None | :class:`str`
            The content to give the message.

        tts: :class:`bool`
            If the message should be sent with text-to-speech. Defaults to False.

        embeds: :class:`list`
            A list of :class:`.EmbedBuilder` instances to send with the message.

        files: :class:`list`
            A list of :class:`.File` instances to send with the message.

        reply: None | :class:`.Message`
            The message to reply to.

        ephemeral: :class:`bool`
            If the response should be ephemeral.

        mentions: :class:`.AllowedMentions`
            The allowed mentions of the message.

        Returns
        -------
        :class:`.Message`
            An instance of the newly sent message.
        """
        org = Route(f"/webhooks/{self.application_id}/{self.token}/messages/@original")

        if content is None and len(embeds) == 0 and len(files) == 0:
            raise ValueError(
                "Message must have at least `content`, `embeds` or `files`."
            ) from None

        elif len(embeds) > 10:
            raise ValueError("Only 10 embeds can be sent per message.") from None

        payload: dict[str, Any] = {
            "content": content,
            "tts": tts,
            "embeds": [e.to_dict() for e in embeds],
            "components": [r.to_dict() for r in rows],
            "allowed_mentions": mentions.to_dict(),
        }

        if reply is not None:
            payload["message_reference"] = reply.reference()

        if ephemeral is not False:
            payload["flags"] = 64

        inter = {"type": InteractionResponse.MESSAGE, "data": payload}

        form: list[dict[Any, Any]] = []
        for index, file in enumerate(files):
            file_data = {
                "content_type": "application/octect-stream",
                "name": f"file-{index}" if index else "file",
                "value": file.source,
                "filename": file.name,
            }

            form.append(file_data)

        await self.client.rest.request(
            "POST",
            Route(f"interactions/{self.snowflake}/{self.token}/callback"),
            json=inter,
            form=form,
        )

        data = await self.client.rest.request("GET", org)
        return Message(self.client, data)
