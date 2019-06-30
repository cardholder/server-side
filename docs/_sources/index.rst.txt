.. Cardholder documentation master file, created by
   sphinx-quickstart on Sun Jun 30 12:06:10 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Cardholder's documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This is the documentation of the backend code of Cardholder.

Models
======

.. autoclass:: lobby.models.Card
   :members:

.. autoclass:: lobby.models.CardSet
   :members:

.. autoclass:: lobby.models.Game
   :members:

Consumer
========

.. autoclass:: lobby.consumers.LobbyListConsumer
   :members:

.. autoclass:: lobby.consumers.LobbyCreateConsumer
   :members:

.. autoclass:: lobby.consumers.LobbyConsumer
   :members:

.. autoclass:: lobby.consumers.MauMauConsumer
   :members:

Lobby
======
.. autoclass:: lobby.lobby.Lobby
   :members:


Player
======
.. autoclass:: lobby.player.Player
   :members:

Lobby list handler
==================
.. automodule:: lobby.lobby_list_handler
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`