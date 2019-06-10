# This is the class for player
import random
from .models import *
from .player import Player
import copy


class MauMau:

    def __init__(self, players):
        self.players = players
        players_len = len(self.players)
        self.current_player = self.players[random.randint(0, players_len)]

        # Get the cards of the game
        game = Game.objects.filter(name="maumau")
        card_set = CardSet.objects.filter(id=game[0].card_set_id)
        cards = card_set.cards.all()
        self.cards = []
        for card in cards:
            self.cards.append(card)

        self.shuffle_cards()
        for player in self.players:
            self.draw_cards(player, 5)

        self.discard_pile = []
        self.discard_pile.append(self.cards.pop())

        self.current_draw_punishment = 1

        self.direction_clock_wise = True

    def shuffle_cards(self):
        random.shuffle(self.cards)

    def draw_cards(self, player, card_number=1):
        if card_number == 1:
            card_number = self.current_draw_punishment

        if player in self.players:
            for i in range(0, card_number):
                if len(self.cards) <= 0:
                    self.shuffle_cards()

                player.cards.append(self.cards.pop())
            self.current_draw_punishment = 1

    def shuffle_discard_pile_into_cards(self):
        discard_card = self.discard_pile.pop()
        self.cards = copy.copy(self.discard_pile)
        self.discard_pile = []
        self.discard_pile.append(discard_card)

    def play_card(self, player, card):
        top_card = self.discard_pile[len(self.discard_pile) - 1]
        if player in self.players:

            if top_card.value == "7" and self.current_draw_punishment > 1:
                if card.value == "7":
                    self.discard_pile.append(card)
                    self.seven_punishment()
                    return True
                elif card.value == "8" and card.symbol == top_card.symbol:
                    self.discard_pile.append(card)
                    self.current_draw_punishment = 1
                    return True
                else:
                    return False
            elif card.value == top_card.value or card.symbol == top_card.symbol or card.value == "10":
                self.discard_pile.append(card)
                self.check_card_action(card)
                return True
            else:
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
        pass

    def choose_next_player(self):
        player_index = self.players.index(self.current_player)
        if self.direction_clock_wise:
            if player_index >= len(self.players):
                self.current_player = self.players[0]
            else:
                self.current_player = self.players[player_index + 1]
        else:
            if player_index <= 0:
                self.current_player = self.players[len(self.players) - 1]
            else:
                self.current_player = self.players[player_index - 1]
