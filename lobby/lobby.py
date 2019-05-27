from .player import Player


# This is the class for a lobby


class Lobby():

    def __init__(self, lobby_id, game, visibility, max_players):
        self.lobby_id = lobby_id
        self.game = game
        self.visibility = visibility
        self.max_players = max_players
        self.players = []

    def add_player(self, player):
        self.players.append(player)
        pass

    def remove_player(self, player):
        self.players.remove(player)
