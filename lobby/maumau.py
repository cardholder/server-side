# This is the class for player
import random
from .models import *
from .player import Player
import copy
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class MauMau:

    def __init__(self, lobby_id, players):
        self.card_wished = None
        self.wait_for_card_wish = False
        self.current_player = None
        self.direction_clock_wise = True

        self.players = []
        self.lobby_id = lobby_id
        if isinstance(players, list):
            for player in players:
                self.players.append(player)
        else:
            self.players.append(players)

        players_len = len(self.players)
        if players_len > 0:
            self.current_player = self.players[random.randint(0, players_len) - 1]

        # Get the cards of the game
        game = Game.objects.get(name="maumau")
        card_set = CardSet.objects.get(id=game.card_set_id)
        self.cards = list(card_set.cards.all())

        self.current_draw_punishment = 1

        self.shuffle_cards()
        for player in self.players:
            self.draw_cards(player, 5)

        self.discard_pile = []
        self.discard_pile.append(self.cards.pop())

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def draw_cards(self, player, card_number=1):

        if not self.wait_for_card_wish:
            return False

        if self.current_draw_punishment == 0:
            self.current_draw_punishment = 1

        if card_number == 1:
            card_number = self.current_draw_punishment

        if player in self.players:
            for i in range(0, card_number):
                if len(self.cards) <= 0:
                    self.shuffle_discard_pile_into_cards()
                card = self.cards.pop()
                player.cards.append(card)
            self.current_draw_punishment = 1
            self.choose_next_player()
            return True
        return False

    def shuffle_discard_pile_into_cards(self):
        if len(self.cards) <= 0:
            discard_card = self.discard_pile.pop()
            self.cards = copy.copy(self.discard_pile)
            self.shuffle_cards()
            self.discard_pile = []
            self.discard_pile.append(discard_card)

    def play_card(self, player, card):
        top_card = self.discard_pile[len(self.discard_pile) - 1]
        if player in self.players and not self.wait_for_card_wish:
            if not player.has_card(card):
                return False

            if player != self.current_player:
                return False

            if self.card_wished is not None:
                return self._play_wished_card(card)

            if top_card.value == "7" and self.current_draw_punishment > 1:
                return self._play_card_on_seven(card, top_card)

            return self._play_normal_card(card, top_card)
        return False

    def check_card_action(self, card):
        if card.value == "7":
            self.seven_punishment()
        elif card.value == "8":
            self.eight_punishment()
        elif card.value == "9":
            self.nine_punishment()
        elif card.value == "B":
            self.jack_wish()

    def seven_punishment(self):
        if self.current_draw_punishment == 1:
            self.current_draw_punishment = 2
        else:
            self.current_draw_punishment = self.current_draw_punishment + 2

    def eight_punishment(self):
        self.choose_next_player()

    def nine_punishment(self):
        self.direction_clock_wise = not self.direction_clock_wise

    def jack_wish(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.lobby_id,
            {"type": "jack.wish", "player": self.current_player.to_json()},
        )
        self.wait_for_card_wish = True

    def choose_next_player(self):
        player_index = self.players.index(self.current_player)
        if self.direction_clock_wise:
            if player_index >= len(self.players) - 1:
                self.current_player = self.players[0]
            else:
                self.current_player = self.players[player_index + 1]
        else:
            if player_index <= 0:
                self.current_player = self.players[len(self.players) - 1]
            else:
                self.current_player = self.players[player_index - 1]

    def _play_card_on_seven(self, card, top_card):
        if card.value == "7":
            self.discard_pile.append(card)
            self.seven_punishment()
        elif card.value == "8" and card.symbol == top_card.symbol:
            self.discard_pile.append(card)
            self.current_draw_punishment = 1
        else:
            return False

        self.remove_card_from_player(card, self.current_player)
        self.choose_next_player()
        return True

    def _play_wished_card(self, card):
        if card.value == "B" or card.value == "10" or card.symbol == self.card_wished:
            self.discard_pile.append(card)
            self.remove_card_from_player(card, self.current_player)
            self.check_card_action(card)
            self.choose_next_player()
            self.card_wished = None
            return True
        else:
            return False

    def _play_normal_card(self, card, top_card):
        if card.value == top_card.value or card.symbol == top_card.symbol or card.value == "10":
            self.discard_pile.append(card)
            self.remove_card_from_player(card, self.current_player)
            self.check_card_action(card)
            if not self.wait_for_card_wish:
                self.choose_next_player()
            return True
        return False

    def get_top_discard_card(self):
        discard_pile_index = len(self.discard_pile) - 1
        return self.discard_pile[discard_pile_index]

    def won_game(self):
        for player in self.players:
            if len(player.cards) == 0:

                return True
        return False

    def remove_card_from_player(self, card, player):
        if player in self.players:
            if card in player.cards:
                player.cards.remove(card)

    def make_card_wish(self, symbol, player):
        if player == self.current_player:
            if symbol in "s c h d":
                self.wait_for_card_wish = False
                self.card_wished = symbol
                self.choose_next_player()
                return True
        return False

    def remove_player_from_game(self, player):
        if player in self.players:
            cards = player.cards
            for card in cards:
                self.cards.append(card)

            self.shuffle_cards()
            player.cards=[]
            if player == self.current_player:
                self.choose_next_player()

            self.players.remove(player)
