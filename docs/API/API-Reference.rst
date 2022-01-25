.. currentmodule:: rin

API-Reference
=============
The API-Reference of the wrapper. Contains all
methods and classes usable.

Meta
----
Misc information about the wrapper.

Version
~~~~~~~
.. data:: __version__
    The current version of the wrapper.

Caching
-------
Things regarding caching and caches in the wrapper.

Cache
~~~~~
.. autoclass:: Cache
    :members:

Cacheable
~~~~~~~~~
.. autoclass:: Cacheable
    :members:

API Interface
-------------
Things in regard to handling and helping use of the API.

GatewayClient
~~~~~~~~~~~~~
.. autoclass:: GatewayClient
    :exclude-members: __init__, on, once
    :members:

    .. autodecorator:: rin.GatewayClient.on
    .. autodecorator:: rin.GatewayClient.once

RESTClient
~~~~~~~~~~
.. autoclass:: RESTClient
    :members:

Route
~~~~~
.. autoclass:: Route
    :members:

Models
------
Models in the wrapper.

Base
~~~~
.. autoclass:: Base
    :members:

User
~~~~
.. autoclass:: User
    :show-inheritance:
    :members:
