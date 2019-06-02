# This is the class for player


class Player:

    def __init__(self, player_id, name, role, channel_layer):
        self.id = player_id
        self.name = name
        self.role = role
        self.channel_layer = channel_layer

    def to_json(self):
        player_dict = {"id": self.id, "name": self.name, "role": self.role}
        return player_dict
