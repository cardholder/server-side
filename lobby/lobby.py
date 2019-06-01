# This is the class for a lobby
import json


class Lobby:

    def __init__(self, lobby_id, game, visibility, max_players):
        self.id = lobby_id
        self.game = game
        self.visibility = visibility
        self.max_players = max_players
        self.players = []

    def add_player(self, player):
        self.players.append(player)
        pass

    def remove_player(self, player):
        self.players.remove(player)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
