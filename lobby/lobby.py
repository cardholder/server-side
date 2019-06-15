# This is the class for a lobby
from .player import Player


class Lobby:

    def __init__(self, lobby_id, game_name, visibility, max_players):
        self.id = lobby_id
        self.game_name = game_name
        self.visibility = visibility
        self.max_players = int(max_players)
        self.players = []
        self.game = None

    def add_player(self, player):
        if len(self.players) < self.max_players:
            self.players.append(player)

    def remove_player(self, player):
        try:
            self.players.remove(player)
        except ValueError:
            pass

    def is_not_empty(self):
        if len(self.players) > 0:
            return True

        return False

    def is_not_full(self):
        if len(self.players) >= self.max_players:
            return False

        return True

    def get_highest_player_id_of_lobby(self):
        player_id = -1
        for player in self.players:
            if player.id > player_id:
                player_id = player.id
        return player_id

    def set_new_leader(self):
        no_leader_in_lobby = True
        for player in self.players:
            if player.is_leader():
                no_leader_in_lobby = False

        if no_leader_in_lobby:
            self.players[0].role = "leader"

    def players_to_json(self):
        player_arr = []
        for player in self.players:
            player_arr.append(player.to_json())
        return player_arr

    def to_json(self):
        lobby_dict = {"id": self.id, "game": self.game_name, "visibility": self.visibility, "max_players": self.max_players,
                      "players": []}
        for player in self.players:
            lobby_dict["players"].append(player.to_json())

        return lobby_dict
