from django.test import TestCase
import lobby.routing
from .lobby_list_handler import lobby_list
import re
from .consumers import *
from .maumau import MauMau


class PlayerTests(TestCase):

    def test_if_player_is_leader(self):
        player = Player(1, "tester", "leader")
        self.assertTrue(player.is_leader())

    def test_if_player_is_not_leader(self):
        player = Player(1, "tester", "player")
        self.assertFalse(player.is_leader())


class LobbyTests(TestCase):

    def test_add_player(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        self.assertEqual(player, lobby_local.players[0])

    def test_add_two_player(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        player_two = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        self.assertEqual(len(lobby_local.players), 2)

    def test_add_adding_more_player_than_max_players(self):
        lobby_local = Lobby(1, "Durak", "public", 1)
        player = Player(1, "tester", "leader")
        player_two = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        self.assertEqual(len(lobby_local.players), 1)

    def test_remove_player(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.remove_player(player)
        self.assertEqual(len(lobby_local.players), 0)

    def test_remove_player_not_existing(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby_local.remove_player(player)
        self.assertRaises(ValueError)

    def test_if_lobby_is_empty(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        self.assertFalse(lobby_local.is_not_empty())

    def test_if_lobby_is_not_empty(self):
        lobby_local = Lobby(1, "Durak", "public", 8)
        player = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        self.assertTrue(lobby_local.is_not_empty())

    def test_if_lobby_is_full(self):
        lobby_local = Lobby(1, "Durak", "public", 1)
        player = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        self.assertFalse(lobby_local.is_not_full())

    def test_if_lobby_is_not_full(self):
        lobby_local = Lobby(1, "Durak", "public", 1)
        self.assertTrue(lobby_local.is_not_full())

    def test_get_highest_player_id_one_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        lobby_local.add_player(player)
        self.assertEqual(lobby_local.get_highest_player_id_of_lobby(), 1)

    def test_get_highest_player_id_two_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        self.assertEqual(lobby_local.get_highest_player_id_of_lobby(), 2)

    def test_get_highest_player_id_no_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        self.assertEqual(lobby_local.get_highest_player_id_of_lobby(), -1)

    def test_new_leader_without_removing_the_leader(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "player")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.set_new_leader()
        self.assertFalse(player_two.is_leader())

    def test_new_leader_without_removing_the_leader_player_two_is_leader(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.set_new_leader()
        self.assertTrue(player_two.is_leader())

    def test_new_leader_without_removing_the_leader_player_is_not_leader(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.set_new_leader()
        self.assertFalse(player.is_leader())

    def test_new_leader_removing_the_leader(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "leader")
        player_two = Player(2, "tester", "player")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.remove_player(player)
        lobby_local.set_new_leader()
        self.assertTrue(player_two.is_leader())

    def test_new_leader_removing_the_leader_player_two_is_leader(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.remove_player(player_two)
        lobby_local.set_new_leader()
        self.assertTrue(player.is_leader())

    def test_player_to_json_no_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        self.assertEqual(lobby_local.players_to_json(), [])

    def test_player_to_json_one_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        lobby_local.add_player(player)
        player_json = [{
                "id": 1,
                "name": "tester",
                "role": "player"
            }]
        self.assertEqual(lobby_local.players_to_json(), player_json)

    def test_player_to_json_two_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
        lobby_local.add_player(player)
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
        self.assertEqual(lobby_local.players_to_json(), player_json)

    def test_to_json_no_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        lobby_json = {
            "id": 1,
            "game": "Durak",
            "visibility": "public",
            "max_players": 2,
            "players": []
        }
        self.assertEqual(lobby_local.to_json(), lobby_json)

    def test_to_json_one_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        lobby_local.add_player(player)
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
        self.assertEqual(lobby_local.to_json(), lobby_json)

    def test_to_json_two_player(self):
        lobby_local = Lobby(1, "Durak", "public", 2)
        player = Player(1, "tester", "player")
        player_two = Player(2, "tester", "leader")
        lobby_local.add_player(player)
        lobby_local.add_player(player_two)
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
        self.assertEqual(lobby_local.to_json(), lobby_json)


class TestLobbyListHandler(TestCase):

    def test_lobby_list_no_lobby(self):
        self.assertEqual(lobby.lobby_list_handler.lobby_list, {})

    def test_create_lobby(self):
        first_id = create_lobby("Durak", "public", 8)
        self.assertEqual(len(lobby.lobby_list_handler.lobby_list), 1)
        remove_lobby(first_id)

    def test_create_two_lobbies(self):
        first_id = create_lobby("Durak", "public", 8)
        second_id = create_lobby("Durak", "public", 8)
        self.assertEqual(len(lobby.lobby_list_handler.lobby_list), 2)
        remove_lobby(first_id)
        remove_lobby(second_id)

    def test_remove_one_lobby(self):
        first_id = create_lobby("Durak", "public", 8)
        second_id = create_lobby("Durak", "public", 8)
        remove_lobby(first_id)
        self.assertEqual(len(lobby.lobby_list_handler.lobby_list), 1)
        remove_lobby(second_id)

    def test_remove_all_lobbies(self):
        first_id = create_lobby("Durak", "public", 8)
        second_id = create_lobby("Durak", "public", 8)
        remove_lobby(first_id)
        remove_lobby(second_id)
        self.assertEqual(len(lobby.lobby_list_handler.lobby_list), 0)

    def test_generate_id(self):
        p = re.compile("\w{7}")
        m = p.match(generate_id())
        self.assertTrue(m)

    def test_check_if_lobby_exists_true(self):
        first_id = create_lobby("Durak", "public", 8)
        self.assertTrue(check_if_lobby_exists(first_id))
        remove_lobby(first_id)

    def test_check_if_lobby_exists_false(self):
        self.assertFalse(check_if_lobby_exists("test_id"))


class TestMauMau(TestCase):
    fixtures = ['cards.json', 'cardsets.json', 'games.json']

    def test_initializing_game_test_card_size(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(len(game.cards), 46)

    def test_initializing_game_players(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(game.players, [player])

    def test_initializing_game_test_discard_pile_size(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(len(game.discard_pile), 1)

    def test_initializing_game_test_current_player_is_player(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(game.current_player, player)

    def test_initializing_game_test_current_player_of_two_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau(players)
        self.assertTrue(game.current_player in players)

    def test_initializing_game_two_players_card_size(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau(players)
        self.assertEqual(len(game.cards), 41)

    def test_initializing_game_direction(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertTrue(game.direction_clock_wise)

    def test_initializing_game_draw_punishment(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(game.current_draw_punishment, 1)

    def test_initializing_game_card_wished(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(game.card_wished, None)

    def test_initializing_game_cards_of_player(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        self.assertEqual(len(game.players[0].cards), 5)

    def test_initializing_game_cards_of_players(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau(players)
        self.assertEqual(len(game.players[1].cards), 5)

    def test_initializing_game_cards_of_players_equal(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau(players)
        self.assertEqual(len(game.players[0].cards), len(game.players[1].cards))

    def test_draw_cards(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        game.players[0].cards = []
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 1)

    def test_draw_two_cards(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        game.players[0].cards = []
        game.draw_cards(player)
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 2)

    def test_draw_two_cards_with_punishment_is_two(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        game.players[0].cards = []
        game.current_draw_punishment = 2
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 2)

    def test_draw_two_cards_with_punishment_is_zero(self):
        player = Player(1, "test", "player")
        game = MauMau(player)
        game.players[0].cards = []
        game.current_draw_punishment = 0
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 1)
