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

Errors
------
Errors used in the wrapper.

HTTPException
~~~~~~~~~~~~~
.. autoexception:: HTTPException
    :exclude-members: __init__, __new__
    :show-inheritance:
    :inherited-members:

BadRequest
~~~~~~~~~~
.. autoexception:: BadRequest
    :exclude-members: __init__, __new__
    :show-inheritance:

Forbidden
~~~~~~~~~
.. autoexception:: Forbidden
    :exclude-members: __init__, __new__
    :show-inheritance:

NotFound
~~~~~~~~
.. autoexception:: NotFound
    :exclude-members: __init__, __new__
    :show-inheritance:

Unauthorized
~~~~~~~~~~~~
.. autoexception:: Unauthorized
    :exclude-members: __init__, __new__
    :show-inheritance:


Builders
--------
Model builders.

IntentsBuilder
~~~~~~~~~~~~~~
.. autoclass:: IntentsBuilder
    :members:

EmbedBuilder
~~~~~~~~~~~~
.. autoclass:: EmbedBuilder
    :members:

MessageBuilder
~~~~~~~~~~~~~~
.. autoclass:: MessageBuilder
    :members:

ANSIBuilder
~~~~~~~~~~~
.. autoclass:: ANSIBuilder
    :members:

.. autoclass:: Mode
    :members:

.. autoclass:: Color
   :members:


Assets
------
Classes/Models used for assets.

File
~~~~
.. autoclass:: File
    :members:


Models
------
Models in the wrapper.

BaseModel
~~~~~~~~~
.. autoclass:: BaseModel
    :members:

Snowflake
~~~~~~~~~
.. autoclass:: Snowflake
    :show-inheritance:
    :members:

AllowedMentions
~~~~~~~~~~~~~~~
.. autoclass:: AllowedMentions
    :members:

Message
~~~~~~~
.. autoclass:: Message
    :show-inheritance:
    :members:

User
~~~~
.. autoclass:: User
    :show-inheritance:
    :members:
