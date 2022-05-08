Getting started
===============

Installation
------------

The first step to using this wrapper is to actually install it. I recommend `poetry` but
you can really use any package manager you wish.

- poetry
    .. code-block:: none

        poetry add rin

- pip
    .. code-block:: none

        pip install rin

Congrats, you have installed rin!

Basic introduction
------------------

In this section I will give a basic introduction to this wrapper.
It is recommended that you know some basic python first of all before started though.

1. Setting event listeners
~~~~~~~~~~~~~~~~~~~~~~~~~~

The main bread & butter of this wrapper is the callback
style of subsribing listeners to events.

A quick little example of setting event listeners.

.. code-block:: python3

    import asyncio
    import rin


    async def main() -> None:
        client = rin.GatewayClient("DISCORD_TOKEN")

        @client.on(rin.Events.READY)
        async def on_ready(user: rin.User) -> None:
            print(f"LOGGED IN AS {user.id}.")

        await client.start()


    asyncio.run(main())

In the example above we set a listener to the event, `READY`. Thus whenever `READY` is
dispatched from the gateway the following callback will be called. There is also many more
was to register a callback. You get different styles of them in this wrapper, E.g :meth:`.GatewayClient.once` and
:meth:`.GatewayClient.collect`

.. note::

   You are required to pass an event to `on(...)` and it's counterparts, E.g `once(...)` and `collect(...)`

Another cool thing about this wrapper, you aren't required to register a callback via the :class:`.GatewayClient`.
You can set a callback with the events itself, for an example.

.. code-block:: python3

   import asyncio
   import rin


   async def main() -> None:
        client = rin.GatewayClient("DISCORD_TOKEN")

        @rin.Events.READY.on()
        async def on_ready(user: rin.User) -> None:
            print(f"LOGGED IN AS {user.id}")

        await client.start()


    asyncio.run(main())

This allows for useful things, such as when you want to register listeners inside of a subclass.
Do note that this is equivalent with the example shown above this example. For simplicity, in future examples
I will be using :meth:`rin.GatewayClient.on`

.. note::

   In-class event registration is only supported by :meth:`.Event.on`, :meth:`.Event.once` and :meth:`.Event.collect`
