# This is the class for a lobby
from .player import Player


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
            lobby_dict["players"].append(player.to_json())

        return lobby_dict

    def players_to_json(self):
        player_arr = []
        for player in self.players:
            player_arr.append(player.to_json())
        return player_arr

    def get_player_with_channel_layer(self, channel_layer):
        for player in self.players:
            if player.channel_layer == channel_layer:
                return player
        return None

    def get_highest_player_id_of_lobby(self):
        player_id = -1
        for player in self.players:
            if player.id > player_id:
                player_id = player.id
        player_id = player_id + 1
        return player_id
