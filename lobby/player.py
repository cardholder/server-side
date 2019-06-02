# This is the class for player


class Player:

    def __init__(self, player_id, name, role, channel_scope):
        self.id = player_id
        self.name = name
        self.role = role
        self.channel_scope = channel_scope

    def to_json(self):
        player_dict = {"id": self.id, "name": self.name, "role": self.role, "channel_scooe": self.channel_scope}
        return player_dict
