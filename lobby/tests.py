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
        self.assertTrue(player.is_leader())

    def test_if_player_is_not_leader(self):
        player = Player(1, "tester", "player")
        self.assertFalse(player.is_leader())


class LobbyTests(TestCase):

    def test_add_player(self):
        lobby = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby.add_player(player)
        self.assertEqual(player, lobby.players[0])

    def test_add_two_player(self):
        lobby = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        player_two = Player(1, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        self.assertEqual(len(lobby.players), 2)

    def test_add_adding_more_player_than_max_players(self):
        lobby = Lobby(1, "Durak", "public", 1)
        player = Player(1, "tester", "leader")
        player_two = Player(1, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        self.assertEqual(len(lobby.players), 1)

    def test_remove_player(self):
        lobby = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby.add_player(player)
        lobby.remove_player(player)
        self.assertEqual(len(lobby.players), 0)

    def test_remove_player_not_existing(self):
        lobby = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby.remove_player(player)
        self.assertRaises(ValueError)

    def test_if_lobby_is_empty(self):
        lobby = Lobby(1, "Durak", "public", 8)
        self.assertFalse(lobby.is_not_empty())

    def test_if_lobby_is_not_empty(self):
        lobby = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby.add_player(player)
        self.assertTrue(lobby.is_not_empty())

    def test_if_lobby_is_full(self):
        lobby = Lobby(1, "Durak", "public", 1)
        player = Player(1, "tester", "leader")
        lobby.add_player(player)
        self.assertFalse(lobby.is_not_full())

    def test_if_lobby_is_not_full(self):
        lobby = Lobby(1, "Durak", "public", 1)
        self.assertTrue(lobby.is_not_full())

    def test_get_highest_player_id_one_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        lobby.add_player(player)
        assert lobby.get_highest_player_id_of_lobby() == 1

    def test_get_highest_player_id_two_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        self.assertEqual(lobby.get_highest_player_id_of_lobby(), 2)

    def test_get_highest_player_id_no_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        print(lobby.get_highest_player_id_of_lobby())
        self.assertEqual(lobby.get_highest_player_id_of_lobby(), -1)

    def test_new_leader_without_removing_the_leader(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "player")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby.set_new_leader()
        self.assertTrue(player.is_leader())
        self.assertFalse(player_two.is_leader())

    def test_new_leader_without_removing_the_leader_player_two_is_leader(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby.set_new_leader()
        self.assertTrue(player_two.is_leader())
        self.assertFalse(player.is_leader())

    def test_new_leader_removing_the_leader(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "player")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby.remove_player(player)
        lobby.set_new_leader()
        self.assertTrue(player_two.is_leader())

    def test_new_leader_removing_the_leader_player_two_is_leader(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby.remove_player(player_two)
        lobby.set_new_leader()
        self.assertTrue(player.is_leader())

    def test_player_to_json_no_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        self.assertEqual(lobby.players_to_json(), [])

    def test_player_to_json_one_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        lobby.add_player(player)
        player_json = [{
                "id": 1,
                "name": "tester",
                "role": "player"
            }]
        self.assertEqual(lobby.players_to_json(), player_json)

    def test_player_to_json_two_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby.add_player(player)
        player_json = [
            {
                "id": 1,
                "name": "tester",
                "role": "player"
            },
            {
                "id": 2,
                "name": "tester",
                "role": "leader"
            }
        ]
        self.assertEqual(lobby.players_to_json(), player_json)

    def test_to_json_no_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        lobby_json = {
            "id": 1,
            "game": "Durak",
            "visibility": "public",
            "max_players": 2,
            "players": []
        }
        self.assertEqual(lobby.to_json(), lobby_json)

    def test_to_json_one_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        lobby.add_player(player)
        lobby_json = {
            "id": 1,
            "game": "Durak",
            "visibility": "public",
            "max_players": 2,
            "players": [
                {
                    "id": 1,
                    "name": "tester",
                    "role": "player"
                }
            ]
        }
        self.assertEqual(lobby.to_json(), lobby_json)

    def test_to_json_two_player(self):
        lobby = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby.add_player(player)
        lobby.add_player(player_two)
        lobby_json = {
            "id": 1,
            "game": "Durak",
            "visibility": "public",
            "max_players": 2,
            "players": [
                {
                    "id": 1,
                    "name": "tester",
                    "role": "player"
                },
                {
                    "id": 2,
                    "name": "tester",
                    "role": "leader"
                }
            ]
        }
        self.assertEqual(lobby.to_json(), lobby_json)


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
