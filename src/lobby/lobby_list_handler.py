# This is the handler for the lobby list.
import random
import string
from .lobby import Lobby

lobby_list = {}


def create_lobby(game, visibility, max_players):
    # generates a random id for new lobby
    lobby_id = generate_id()
    while check_if_lobby_exists(lobby_id):
        # generates a new lobby_id if it already exists
        lobby_id = generate_id()

    lobby = Lobby(lobby_id, game, visibility, max_players)
    lobby_list[str(lobby_id)] = lobby
    return lobby_id


def remove_lobby(lobby_id):
    del lobby_list[str(lobby_id)]


def generate_id(string_length=7):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))


def check_if_lobby_exists(lobby_id):
    return str(lobby_id) in lobby_list
