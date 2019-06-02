# This is the class for player


class Player:

    def __init__(self, player_id, name, role):
        self.id = player_id
        self.name = name
        self.role = role

    def to_json(self):
        player_dict = {"id": self.id, "name": self.name, "role": self.role}
        return player_dict
