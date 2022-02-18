from __future__ import annotations

from typing import TYPE_CHECKING, Any

import attr

from ...rest import Route
from ..assets import File
from ..message import ActionRow, AllowedMentions, Message
from ..snowflake import Snowflake
from .embed import EmbedBuilder

if TYPE_CHECKING:
    from ...client import GatewayClient

__all__ = ("MessageBuilder",)


@attr.s(slots=True)
class MessageBuilder:
    """A helper class used to add messaging functionality.

    This class is intended to be used both internally and in frontend.
    It is encouraged to construct this class when sending a message without an object.
    This allows for users to not have a full object to send messages.

    Attributes
    ----------
    client: :class:`.GatewayClient`
        The client being used to send a message.

    snowflake: :class:`.Snowflake`
        The snowflake of the channel to send a message to.
    """

    client: GatewayClient = attr.field(repr=False)
    snowflake: Snowflake | int = attr.field(repr=True)

    def set_snowflake(self, snowflake: Snowflake) -> None:
        """A helper method ued to set the snowflake of the instance.
        Useful for classes such as a DM Channel.

        Parameters
        ----------
        snowflake: :class:`.Snowflake`
            The snowflake to set.
        """
        self.snowflake = snowflake

    async def send(
        self,
        content: None | str = None,
        tts: bool = False,
        embeds: list[EmbedBuilder] = [],
        files: list[File] = [],
        rows: list[ActionRow] = [],
        reply: None | Message = None,
        mentions: AllowedMentions = AllowedMentions(),
    ) -> Message:
        """Sends a message into the channel corresponding to the passed in :class:`.Snowflake`.

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

        mentions: :class:`.AllowedMentions`
            The allowed mentions of the message.

        Returns
        -------
        :class:`.Message`
            An instance of the newly sent message.
        """

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

        form: list[dict[Any, Any]] = []
        for index, file in enumerate(files):
            file_data = {
                "content_type": "application/octect-stream",
                "name": f"file-{index}" if index else "file",
                "value": file.source,
                "filename": file.name,
            }

            form.append(file_data)

        data = await self.client.rest.request(
            "POST",
            Route(f"channels/{self.snowflake}/messages", channel_id=self.snowflake),
            json=payload,
            form=form,
        )

        return Message(self.client, data)
