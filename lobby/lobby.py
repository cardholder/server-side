# This is the class for a lobby
import json


class Lobby:

    def __init__(self, lobby_id, game, visibility, max_players):
        self.id = lobby_id
        self.game = game
        self.visibility = visibility
        self.max_players = int(max_players)
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)

    def is_not_empty(self):
        if len(self.players) > 0:
            return True

        return False

    def to_json(self):
        lobby_dict = {"id": self.id, "game": self.game, "visibility": self.visibility, "max_players": self.max_players,
                      "players": []}
        for player in self.players:
            lobby_dict["players"].append(player.__dict__)

        return lobby_dict
