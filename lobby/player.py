# This is the class for player


class Player:

    def __init__(self, player_id, name, role):
        self.id = int(player_id)
        self.name = name
        self.role = role
        self.cards = []

    def to_json(self):
        player_dict = {"id": self.id, "name": self.name, "role": self.role, "card_amount": len(self.cards)}
        return player_dict

    def is_leader(self):
        return self.role == "leader"

    def has_card(self, card):
        return card in self.cards
