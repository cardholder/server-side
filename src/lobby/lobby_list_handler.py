# This is the handler for the lobby list.
import random
import string
from .lobby import Lobby

lobbylist = set()


def create_lobby(game, visibility, max_players):
    # generates a random id for new lobby
    lobby_id = generate_id()
    lobby = Lobby(lobby_id, game, visibility, max_players)
    lobbylist.add(lobby)
    return lobby_id


def remove_lobby(lobby):
    lobbylist.remove(lobby)


def generate_id(string_length=7):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))
