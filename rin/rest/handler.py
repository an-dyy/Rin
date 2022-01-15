from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp

from .errors import BadRequest, Forbidden, NotFound, Unauthorized
from .ratelimiter import RatelimitedClientResponse, Ratelimiter

if TYPE_CHECKING:
    from ..client import GatewayClient
    from ..gateway import Gateway

__all__ = ("RESTClient", "Route")


class Route:
    """Route used for RESTful requests.

    This class is used in the wrapper where requests are made.
    The wrapper does not have a centralized part that has all predefined
    RESTful calls. The wrapper will instead utilize Routes in class depedent
    methods to make their respective requests.

    Parameters
    ----------
    endpoint: :class:`str`
        The endpoint of the Route.

    version: :class:`str`
        The version of the RESTful API to use.

    channel_id: Optional[:class:`int`]
        The channel ID being used. This is used for bucket specificity.

    guild_id: Optional[:class:`int`]
        The guild ID being used. This is used for bucket specificity.

    webhook_id: Optional[:class:`int`]
        The webhook ID being used. This is used for bucket specificity.

    webhook_token: Optional[:class:`str`]
        The webhook token being used. This is used for bucket specificity.

    Attributes
    ----------
    endpoint: :class:`str`
        The fully formed endpoint of the route.

    lock: :class:`asyncio.Lock`
        The lock used for the bucket once depleted. Used in
        tandem with the concurrent request ratelimit system. Allowing safe
        concurrent requests.

    channel_id: Optional[:class:`int`]
        The channel ID being used. This is used for bucket specificity.

    guild_id: Optional[:class:`int`]
        The guild ID being used. This is used for bucket specificity.

    webhook_id: Optional[:class:`int`]
        The webhook ID being used. This is used for bucket specificity.

    webhook_token: Optional[:class:`str`]
        The webhook token being used. This is used for bucket specificity.
    """

    __slots__ = (
        "endpoint",
        "lock",
        "channel_id",
        "guild_id",
        "webhook_id",
        "webhook_token",
    )

    BASE = "https://discord.com/api/v{0}/"

    def __init__(self, endpoint: str, *, version: str = "9", **kwargs: Any) -> None:
        self.endpoint = Route.BASE.format(version) + endpoint
        self.lock = asyncio.Lock()

        self.channel_id: None | int = kwargs.get("channel_id")
        self.guild_id: None | int = kwargs.get("guild_id")
        self.webhook_id: None | int = kwargs.get("webhook_id")
        self.webhook_token: None | str = kwargs.get("webhookd_token")

    @property
    def bucket(self) -> str:
        """The bucket of the Route."""
        return f"{self.channel_id}/{self.guild_id}/{self.webhook_id}/{self.endpoint}"


class RESTClient:
    """The class used to make RESTful API requests.

    This class implements requesting which works in tandem
    with the concurrent request ratelimit system. Allows for safe requesting
    and bucket depletion sanity.

    Parameters
    ----------
    token: :class:`str`
        The token used for authorization.

    client: :class:`.GatewayClient`
        The client being used.

    Attributes
    ----------
    session: :class:`aiohttp.ClientSession`
        The session assiocated with the RESTClient.

    token: :class:`str`
        The token used for authorization.

    client: :class:`.GatewayClient`
        The client being used.

    semaphores: dict[str, :class:`asyncio.Semaphore`]
        The semaphores used for each bucket. This is used to
        ensure safety and allowing concurrent requests.
    """

    __slots__ = ("session", "token", "client", "semaphores")

    GATEWAY_TYPE: ClassVar[type[Gateway]]
    ERRORS: ClassVar[dict[int, Any]] = {
        400: BadRequest,
        401: Unauthorized,
        403: Forbidden,
        404: NotFound,
    }

    def __init__(self, token: str, client: GatewayClient) -> None:
        self.session: aiohttp.ClientSession
        self.token = token
        self.client = client

        self.semaphores: dict[str, asyncio.Semaphore] = {
            "global": asyncio.Semaphore(50)
        }

    async def _create_session(self) -> aiohttp.ClientSession:
        if hasattr(self, "session"):
            return self.session

        return aiohttp.ClientSession(
            ws_response_class=RESTClient.GATEWAY_TYPE,
            response_class=RatelimitedClientResponse,
            loop=self.client.loop,
        )

    async def connect(self, url: str) -> Gateway:
        """Makes a connection to the gateway.

        Parameters
        ----------
        url: :class:`str`
            The url of the gateway.

        Returns
        -------
        :class:`.Gateway`
            The gateway after connection is made.
        """
        if not hasattr(self, "session"):
            self.session = await self._create_session()

        return await self.session.ws_connect(url)  # type: ignore

    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> RatelimitedClientResponse:
        self.session = await self._create_session()

        return await self.session.request(  # type: ignore
            method,
            endpoint,
            headers={"Authorization": f"Bot {self.token}"},
            **kwargs,
        )

    async def request(self, method: str, route: Route, **kwargs: Any) -> Any:
        """Makes a request to the Route.

        A safe request method of the client. Ensures bucket depletion is safe
        along with global ratelimits.

        Parameters
        ----------
        method: :class:`str`
            The method to make the request with, E.g `"GET"`.

        route: :class:`.Route`
            The route to use for the request

        kwargs: Any
            Extra things to pass to the request, E.g `json=payload`.

        Raises
        ------
        :exc:`.HTTPException`
            Something went wrong with the request.

        Returns
        -------
        Any:
            The return data from the request.
        """
        async with Ratelimiter(self, route) as handler:
            return await handler.request(method, **kwargs)
