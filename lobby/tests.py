from django.test import TestCase
import lobby.routing
from .lobby_list_handler import lobby_list
import re
from .consumers import *
from .maumau import MauMau
from .models import Card


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
                "role": "player",
                "card_amount": 0
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
                "role": "player",
                "card_amount": 0
            },
            {
                "id": 2,
                "name": "tester",
                "role": "leader",
                "card_amount": 0
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
                    "role": "player",
                    "card_amount": 0
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
                    "role": "player",
                    "card_amount": 0
                },
                {
                    "id": 2,
                    "name": "tester",
                    "role": "leader",
                    "card_amount": 0
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
        game = MauMau("lobby", player)
        self.assertEqual(len(game.cards), 46)

    def test_initializing_game_players(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(game.players, [player])

    def test_initializing_game_test_discard_pile_size(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(len(game.discard_pile), 1)

    def test_initializing_game_test_current_player_is_player(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(game.current_player, player)

    def test_initializing_game_test_current_player_of_two_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau("lobby", players)
        self.assertTrue(game.current_player in players)

    def test_initializing_game_two_players_card_size(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau("lobby", players)
        self.assertEqual(len(game.cards), 41)

    def test_initializing_game_direction(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertTrue(game.direction_clock_wise)

    def test_initializing_game_draw_punishment(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(game.current_draw_punishment, 1)

    def test_initializing_game_card_wished(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(game.card_wished, None)

    def test_initializing_game_cards_of_player(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        self.assertEqual(len(game.players[0].cards), 5)

    def test_initializing_game_cards_of_players(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau("lobby", players)
        self.assertEqual(len(game.players[1].cards), 5)

    def test_initializing_game_cards_of_players_equal(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test2", "player")
        players = [player, player_two]
        game = MauMau("lobby", players)
        self.assertEqual(len(game.players[0].cards), len(game.players[1].cards))

    def test_draw_cards(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.players[0].cards = []
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 1)

    def test_draw_two_cards(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.players[0].cards = []
        game.draw_cards(player)
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 2)

    def test_draw_two_cards_with_punishment_is_two(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.players[0].cards = []
        game.current_draw_punishment = 2
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 2)

    def test_draw_two_cards_with_punishment_is_zero(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.players[0].cards = []
        game.current_draw_punishment = 0
        game.draw_cards(player)
        self.assertEqual(len(game.players[0].cards), 1)

    def test_shuffle_discard_pile_into_cards_not_empty_cards(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.shuffle_discard_pile_into_cards()
        self.assertEqual(len(game.cards), 46)

    def test_shuffle_discard_pile_into_cards_empty_cards(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        game.cards = []
        game.shuffle_discard_pile_into_cards()
        self.assertEqual(len(game.cards), 0)

    def test_shuffle_discard_pile_into_cards_empty_cards_top_card_is_equal_as_before(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        card = game.discard_pile[0]
        game.cards = []
        game.shuffle_discard_pile_into_cards()
        self.assertEqual(game.discard_pile[0], card)

    def test_shuffle_discard_pile_into_cards_empty_cards_three_cards_in_discard_pile(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        card_one = game.cards.pop()
        card_two = game.cards.pop()
        game.cards = []
        game.discard_pile.append(card_one)
        game.discard_pile.append(card_two)
        game.shuffle_discard_pile_into_cards()
        self.assertEqual(len(game.cards), 2)

    def test_shuffle_discard_pile_into_cards_empty_cards_three_cards_in_discard_pile_size_of_discard_pile(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", player)
        card_one = game.cards.pop()
        card_two = game.cards.pop()
        game.cards = []
        game.discard_pile.append(card_one)
        game.discard_pile.append(card_two)
        game.shuffle_discard_pile_into_cards()
        self.assertEqual(len(game.discard_pile), 1)

    def test_choose_next_player_first_players_turn_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = game.players[0]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[1])

    def test_choose_next_player_second_players_turn_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = game.players[1]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[2])

    def test_choose_next_player_third_players_turn_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = game.players[2]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[0])

    def test_choose_next_player_first_players_turn_counter_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.direction_clock_wise = False
        game.current_player = game.players[0]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[2])

    def test_choose_next_player_second_players_turn_counter_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.direction_clock_wise = False
        game.current_player = game.players[1]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[0])

    def test_choose_next_player_third_players_turn_counter_clockwise(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.direction_clock_wise = False
        game.current_player = game.players[2]
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[1])

    def test_seven_punishment_once(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.seven_punishment()
        self.assertEqual(game.current_draw_punishment, 2)

    def test_seven_punishment_twice(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.seven_punishment()
        game.seven_punishment()
        self.assertEqual(game.current_draw_punishment, 4)

    def test_seven_punishment_three_times(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.seven_punishment()
        game.seven_punishment()
        game.seven_punishment()
        self.assertEqual(game.current_draw_punishment, 6)

    def test_eight_punishment(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = game.players[0]
        game.eight_punishment()
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[2])

    def test_nine_punishment_clockwise(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player, ])
        game.nine_punishment()
        self.assertFalse(game.direction_clock_wise)

    def test_nine_punishment_counter_clockwise(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player, ])
        game.direction_clock_wise = False
        game.nine_punishment()
        self.assertTrue(game.direction_clock_wise)

    def test_check_action_seven_card(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        card = Card.objects.get(value="7", symbol="c")
        game.check_card_action(card)
        self.assertEqual(game.current_draw_punishment, 2)

    def test_check_action_eight_card(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = game.players[0]
        card = Card.objects.get(value="8", symbol="c")
        game.check_card_action(card)
        game.choose_next_player()
        self.assertEqual(game.current_player, game.players[2])

    def test_check_action_nine_card(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        card = Card.objects.get(value="9", symbol="c")
        game.check_card_action(card)
        self.assertFalse(game.direction_clock_wise)

    def test_play_card_colour_on_colour(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="c")
        card_two = Card.objects.get(value="3", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_play_card_colour_on_colour_check_next_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="c")
        card_two = Card.objects.get(value="3", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_player, player_two)

    def test_play_card_value_on_value(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="3", symbol="s")
        card_two = Card.objects.get(value="3", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_play_card_colour_on_seven(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="2", symbol="s")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertFalse(game.play_card(player, card_two))

    def test_play_card_colour_on_seven_check_next_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="2", symbol="s")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertFalse(game.play_card(player, card_two))
        self.assertEqual(game.current_player, player)

    def test_play_card_seven_on_seven(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="7", symbol="c")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_draw_punishment, 4)

    def test_play_card_seven_on_seven_check_next_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="7", symbol="c")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_draw_punishment, 4)
        self.assertEqual(game.current_player, player_two)

    def test_play_card_eight_on_seven(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="8", symbol="s")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_draw_punishment, 1)

    def test_play_card_eight_on_seven_check_next_player(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="8", symbol="s")
        game.current_draw_punishment = 2
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_draw_punishment, 1)
        self.assertEqual(game.current_player, player_two)

    def test_play_card_on_seven_no_punishment(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="2", symbol="s")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_play_card_seven_on_seven_no_punishment(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="7", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_draw_punishment, 2)

    def test_play_card_eight_on_seven_no_punishment(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = player
        card_one = Card.objects.get(value="7", symbol="s")
        card_two = Card.objects.get(value="8", symbol="s")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_player, player_three)

    def test_play_card_eight_on_colour(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="s")
        card_two = Card.objects.get(value="8", symbol="s")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_player, player_three)

    def test_play_card_nine_on_colour(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="s")
        card_two = Card.objects.get(value="9", symbol="s")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.current_player, player_three)

    def test_play_card_ten_on_colour(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="s")
        card_two = Card.objects.get(value="10", symbol="s")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_play_card_ten_on_wrong_colour(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        player_three = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two, player_three])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="s")
        card_two = Card.objects.get(value="10", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_play_card_player_not_known(self):
        player = Player(1, "test", "player")
        player_two = Player(2, "test", "player")
        game = MauMau("lobby", [player])
        game.current_player = player
        card_one = Card.objects.get(value="2", symbol="s")
        card_two = Card.objects.get(value="2", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertFalse(game.play_card(player_two, card_two))

    def test_play_card_card_wished(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.current_player = player
        card_one = Card.objects.get(value="B", symbol="s")
        card_two = Card.objects.get(value="2", symbol="c")
        game.card_wished = "c"
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_card_wished_is_none(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.current_player = player
        card_one = Card.objects.get(value="B", symbol="s")
        card_two = Card.objects.get(value="2", symbol="c")
        game.card_wished = "c"
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertEqual(game.card_wished, None)

    def test_card_to_json(self):
        card_one = Card.objects.get(value="A", symbol="c")
        card_one_json = card_one.to_json
        compare_json = {
            "id": 1,
            "value": "A",
            "symbol": "c"
        }
        self.assertEqual(card_one_json, compare_json)

    def test_cards_to_json(self):
        card_one = Card.objects.get(value="A", symbol="s")
        card_two = Card.objects.get(value="A", symbol="c")
        cards = [card_one, card_two]
        compare_json = {"cards": [
            {
                "id": 3,
                "value": "A",
                "symbol": "s"
            },
            {
                "id": 1,
                "value": "A",
                "symbol": "c"
            }
        ]}
        self.assertEqual({"cards": MauMauConsumer.cards_to_json(cards)}, compare_json)

    def test_play_card_value_on_value_check_discard_card(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="3", symbol="s")
        card_two = Card.objects.get(value="3", symbol="c")
        game.discard_pile.append(card_one)
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        discard_card = game.get_top_discard_card()
        self.assertEqual(game.current_player, player_two)
        self.assertEqual(discard_card, card_two)

    def test_play_card_player_has_played_card(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="3", symbol="s")
        card_two = Card.objects.get(value="3", symbol="c")
        game.discard_pile.append(card_one)
        player.cards = []
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))
        self.assertFalse(card_two in player.cards)

    def test_play_ten_when_card_wished(self):
        player = Player(1, "test", "player")
        player_two = Player(1, "test", "player")
        game = MauMau("lobby", [player, player_two])
        game.current_player = player
        card_one = Card.objects.get(value="B", symbol="s")
        card_two = Card.objects.get(value="10", symbol="c")
        game.card_wished = 'h'
        game.discard_pile.append(card_one)
        player.cards = []
        player.cards.append(card_two)
        self.assertTrue(game.play_card(player, card_two))

    def test_next_player_with_only_one_player(self):
        player = Player(1, "test", "player")
        game = MauMau("lobby", [player])
        game.current_player = player
        game.choose_next_player()
        self.assertTrue(game.current_player, player)
