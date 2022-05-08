from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable


@runtime_checkable
class _EmbedItem(Protocol):
    data: dict[Any, Any]

    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs
        self.__dict__.update(kwargs)


if TYPE_CHECKING:

    class EmbedFooter(_EmbedItem):
        data: dict[Any, Any]

        text: str
        icon_url: None | str

    class EmbedAuthor(_EmbedItem):
        data: dict[Any, Any]

        name: str
        url: None | str
        icon_url: None | str

    class EmbedProvider(_EmbedItem):
        data: dict[Any, Any]

        name: None | str
        url: None | str

    class EmbedVideo(_EmbedItem):
        data: dict[Any, Any]

        url: str
        height: None | int
        width: None | int

    class EmbedImage(_EmbedItem):
        data: dict[Any, Any]

        url: str
        height: None | int
        width: None | int

    class EmbedThumbnail(_EmbedItem):
        data: dict[Any, Any]

        url: str
        height: None | int
        width: None | int

    class EmbedField(_EmbedItem):
        data: dict[Any, Any]

        name: str
        value: str
        inline: bool


class EmbedItem:
    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs
        self.__dict__.update(kwargs)


__all__ = ("EmbedBuilder",)


class EmbedBuilder:
    def __init__(self, **kwargs: Any) -> None:
        self.data = kwargs
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls: type[EmbedBuilder], data: dict[Any, Any]) -> EmbedBuilder:
        """Creates an Embed object from a dict.

        Parameters
        ----------
        data: :class:`dict`
            The data to create the embed from

        Returns
        -------
        :class:`.EmbedBuilder`
            A created embed from the dict.
        """
        return cls(**data)

    def to_dict(self) -> dict[Any, Any]:
        """Creates a dict representing the embed.

        Returns
        ------
        :class:`dict`
            The dict representing the embed.
        """
        payload = self.data.copy()

        for name, item in payload.items():
            if isinstance(item, _EmbedItem):
                payload[name] = {**item.data}

                continue

            elif isinstance(item, list):
                if not all(isinstance(obj, _EmbedItem) for obj in item):
                    continue

                data: list[dict[Any, Any]] = []
                item: list[EmbedField]
                for field in item:
                    field: EmbedField

                    data.append({**field.data})

                payload[name] = data

        return payload

    @property
    def title(self) -> None | str:
        """The embed's title."""
        return self.data.get("title")

    @title.setter
    def title(self, title: str) -> None:
        """Set the embed's title.

        Characters cannot be more than 256 characters.

        Parameters
        ----------
        title: :class:`str`
            The title to set

        Raises
        ------
        :exc:`ValueError`
            The given title was longer that 256 characters.
        """
        if len(title) > 256:
            raise ValueError("Title cannot have more than 256 characters")

        self.data["title"] = title

    @property
    def description(self) -> None | str:
        """The embed's description."""
        return self.data.get("description")

    @description.setter
    def description(self, description: str) -> None:
        """Set the embed's description.

        Characters cannot be more than 4096 characters.

        Parameters
        ----------
        description: :class:`str`
            The description to set

        Raises
        ------
        :exc:`ValueError`
            The description was longer than 4096 characters.
        """
        if len(description) > 4096:
            raise ValueError("Description cannot have more than 4096 characters")

        self.data["description"] = description

    @property
    def url(self) -> None | str:
        """The embed's url."""
        return self.data.get("url")

    @url.setter
    def url(self, url: str) -> None:
        """Sets the embed's url.

        Parameters
        ----------
        url: :class:`str`
            The url to set
        """
        self.data["url"] = url

    @property
    def timestamp(self) -> None | datetime:
        """The embed's timestamp."""
        return self.data.get("timestamp")

    @timestamp.setter
    def timestamp(self, timestamp: datetime) -> None:
        """Sets the embed's timestamp.

        Parameters
        ----------
        timestamp: :class:`datetime.datetime`
            The datetime to use as the timestamp
        """
        self.data["timestamp"] = timestamp

    @property
    def color(self) -> None | int:
        """The embed's color."""
        return self.data.get("color")

    @color.setter
    def color(self, color: int) -> None:
        """Sets the embed's color.

        Parameters
        ----------
        color: :class:`int`
            The color to set
        """
        self.data["color"] = color

    @property
    def footer(self) -> None | EmbedFooter:
        """The embed's footer."""
        return self.data.get("footer")

    def set_footer(self, text: str, icon_url: None | str = None) -> None:
        """Sets the embed's footer.

        Parameters
        ----------
        text: :class:`str`
            The text of the footer

        icon_url: None | :class:`str`
            The icon url of the footer
        """
        self.data["footer"] = EmbedItem(text=text, icon_url=icon_url)

    @property
    def image(self) -> None | EmbedImage:
        """The embed's image."""
        return self.data.get("image")

    def set_image(
        self, url: str, height: None | int = None, width: None | int = None
    ) -> None:
        """Sets the embed's image.

        Parameters
        ----------
        url: :class:`str`
            The url of the image.

        height: None | :class``int`
            The height of the image.

        width: None | :class:`int`
            The width of the image.
        """
        self.data["image"] = EmbedItem(url=url, height=height, width=width)

    @property
    def thumbnail(self) -> None | EmbedThumbnail:
        """The embed's thumbnail."""
        return self.data.get("thumbnail")

    def set_thumbnail(
        self, url: str, height: None | int = None, width: None | int = None
    ) -> None:
        """Sets the embed's thumbnail.

        Parameters
        ----------
        url: :class:`str`
            The url of the image.

        height: None | :class:`int`
            The height of the thumbnail.

        width: None | :class:`int`
            The width of the thumbnail.
        """
        self.data["thumbnail"] = EmbedItem(url=url, height=height, width=width)

    @property
    def video(self) -> None | EmbedVideo:
        """The embed's video."""
        return self.data.get("video")

    def set_video(
        self, url: str, height: None | int = None, width: None | int = None
    ) -> None:
        """Sets the embed's video.

        Parameters
        ----------
        url: :class:`str`
            The url of the video.

        height: None | :class:`int`
            The height of the video.

        width: None | :class:`int`
            The width of the video.
        """
        self.data["thumbnail"] = EmbedItem(url=url, height=height, width=width)

    @property
    def provider(self) -> None | EmbedProvider:
        """The embed's provider."""
        return self.data.get("provider")

    def set_provider(self, name: None | str = None, url: None | str = None) -> None:
        """Sets the embed's provider.

        Parameters
        ----------
        name: None | :class:`str`
            The name of the provider.

        url: None | :class:`str`
            The url of the provider.
        """
        self.data["provider"] = EmbedItem(name=name, url=url)

    @property
    def author(self) -> None | EmbedAuthor:
        """The embed's author."""
        return self.data.get("author")

    def set_author(
        self, name: str, url: None | str = None, icon_url: None | str = None
    ) -> None:
        """Sets the embed's author.

        Parameters
        ----------
        name: :class:`str`
            The name of the author.

        url: None | :class:`str`
            The url of the author.

        icon_url: None | :class:`str`
            The icon url of the author.
        """
        self.data["author"] = EmbedItem(name=name, url=url, icon_url=icon_url)

    @property
    def fields(self) -> None | list[EmbedField]:
        """The embed's fields."""
        return self.data.get("fields")

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        """Adds a field to the embed.

        Parameters
        ----------
        name: :class:`str`
            The fields name

        value: :class:`str`
            The value of the field

        inline: :class:`bool`
            Whether or not the field is inline
        """
        self.data.setdefault("fields", []).append(
            EmbedItem(name=name, value=value, inline=inline)
        )
