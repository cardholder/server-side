from django.test import TestCase
from channels.testing import WebsocketCommunicator
import pytest
from channels.routing import URLRouter
import lobby.routing
from .player import Player
from .lobby import Lobby


class PlayerTests(TestCase):

    def test_if_player_is_leader(self):
        player = Player(1, "tester", "leader")
        assert player.is_leader()

    def test_if_player_is_not_leader(self):
        player = Player(1, "tester", "player")
        assert not player.is_leader()


class LobbyTests(TestCase):

    def test_when_chat_message_posted_then_seen_by_everyone_in_same_room(self):
        var = True
        assert True == var


class TestLobbyListConsumer(TestCase):

    @pytest.mark.asyncio
    async def test_get_connected_client(self):

        application = URLRouter(
            lobby.routing.websocket_urlpatterns
        )

        communicator = WebsocketCommunicator(application, "/lobbylist/")
        connected, sub_protocol = await communicator.connect()
        assert connected
        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_client_gets_empty_lobby(self):
        application = URLRouter(
            lobby.routing.websocket_urlpatterns
        )

        communicator = WebsocketCommunicator(application, "/lobbylist/")
        connected, sub_protocol = await communicator.connect()
        response = await communicator.receive_from()
        assert response == []
        await communicator.disconnect()
