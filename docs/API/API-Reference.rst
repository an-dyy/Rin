.. currentmodule:: rin

API-Reference
=============
The API-Reference of the wrapper. Contains all
methods and classes usable.

Version
-------
.. data:: __version__
    The current version of the wrapper.

Cacheable
---------
.. autoclass:: Cacheable
    :members:

Cache
-----
.. autoclass:: Cache
    :members:

GatewayClient
-------------
.. autoclass:: GatewayClient
    :exclude-members: __init__, on, once
    :members:

    .. autodecorator:: rin.GatewayClient.on
    .. autodecorator:: rin.GatewayClient.once

User
----
.. autoclass:: User
    :show-inheritance:
    :members:
