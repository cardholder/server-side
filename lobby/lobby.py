class Lobby:
    """
    This is the class for creating a lobby.
    """

    def __init__(self, lobby_id, game_name, visibility, max_players):
        """
        This is the Constructor of the lobby. A game associated to a lobby. Game is None when initializing a lobby.

        :param lobby_id: Lobby_id of the lobby
        :param game_name: Name of the game
        :param visibility: Visibility of lobby, "private" or "public"
        :param max_players: Maximum number of players that can join this lobby
        """
        self.id = lobby_id
        self.game_name = game_name
        self.visibility = visibility
        self.max_players = int(max_players)
        self.players = []
        self.game = None

    def add_player(self, player):
        """
        Adds a player to the lobby.

        :param player: Player that is added to the lobby
        """
        if len(self.players) < self.max_players:
            self.players.append(player)

    def remove_player(self, player):
        """
        Removes a player from the lobby.

        :param player: Player that is removed from the lobby
        """
        try:
            self.players.remove(player)
        except ValueError:
            pass

    def is_not_empty(self):
        """
        Checks if lobby is not empty and returns it.
        :return: True when lobby is not empty as Boolean
        """
        if len(self.players) > 0:
            return True

        return False

    def is_not_full(self):
        """
        Checks if the lobby is not full and returns it.
        :return: True when lobby is not full as Boolean
        """
        if len(self.players) >= self.max_players:
            return False

        return True

    def get_highest_player_id_of_lobby(self):
        """
        Gets the highest player id from lobby
        :return: lobby_id as int. Returns -1, when no player is in lobby.
        """

        # Minimum id value is 0 so setting to -1 is fine.
        player_id = -1
        for player in self.players:
            if player.id > player_id:
                player_id = player.id
        return player_id

    def set_new_leader(self):
        """
        Sets a new leader in lobby, when no leader is in the current lobby.
        """
        no_leader_in_lobby = True
        for player in self.players:
            if player.is_leader():
                no_leader_in_lobby = False

        if no_leader_in_lobby:
            self.players[0].role = "leader"

    def players_to_json(self):
        """
        Gets players of lobby and returns them as a dictionary
        :return: list of player as dict
        """
        player_arr = []
        for player in self.players:
            player_arr.append(player.to_json())
        return player_arr

    def to_json(self):
        """
        Returns the lobby as dictionary
        :return: lobby as dict
        """
        lobby_dict = {"id": self.id, "game": self.game_name, "visibility": self.visibility, "max_players": self.max_players,
                      "players": []}
        for player in self.players:
            lobby_dict["players"].append(player.to_json())

        return lobby_dict
