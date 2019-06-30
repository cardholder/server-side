
class Player:
    """
    Class for a player.
    """

    def __init__(self, player_id, name, role):
        """
        Constructor for Player. Cards are also initialized but empty until player is playing a game.
        :param player_id: id for player
        :param name: name of player
        :param role: role of player. "leader" or "player"
        """
        self.id = int(player_id)
        self.name = name
        self.role = role
        self.cards = []

    def to_json(self):
        """
        Creates a dict from player with his card_amount. Returns this dict.
        :return: player json as dict
        """
        player_dict = {"id": self.id, "name": self.name, "role": self.role, "card_amount": len(self.cards)}
        return player_dict

    def is_leader(self):
        """
        Returns if the player is a leader.
        :return: True, when player is "leader" as Boolean
        """
        return self.role == "leader"

    def has_card(self, card):
        """
        Check if player has the card in his cards array.
        :param card: card that is compared to
        :return: True, when card exists in cards array as Boolean
        """
        return card in self.cards
