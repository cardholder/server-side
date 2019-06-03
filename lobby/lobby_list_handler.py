# This is the handler for the lobby list.
import random
import string
from .lobby import Lobby
from .player import Player
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    # Generate a random string of fixed length
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(string_length))


def check_if_lobby_exists(lobby_id):
    return str(lobby_id) in lobby_list


def update_lobby(lobby_id):
    channel_layer = get_channel_layer()
    lobby = lobby_list[str(lobby_id)]
    players = lobby.players_to_json()

    async_to_sync(channel_layer.group_send)(
        lobby_id,
        {"type": "update.lobby", "players": players},
    )
    async_to_sync(channel_layer.group_send)(
        "lobbylist",
        {"type": "update.lobby", "lobby": lobby.to_json()},
    )


def send_remove_lobby(lobby_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "lobbylist",
        {"type": "remove.lobby", "lobby_id": lobby_id},
    )


def send_lobby_is_full(lobby_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        lobby_id,
        {"type": "lobby.full", "message": "Lobby ist voll!"},
    )


def add_player_to_lobby(lobby_id, name):
    lobby = lobby_list[str(lobby_id)]

    if not lobby.is_not_full():
        send_lobby_is_full(lobby_id)
        return None, None

    player_id = lobby.get_highest_player_id_of_lobby()
    if player_id == 0:
        role = "leader"
    else:
        role = "player"

    player = Player(player_id, name, role)
    lobby.add_player(player)
    update_lobby(lobby_id)

    return lobby_id, player


def remove_player_from_lobby(lobby_id, player):
    lobby = lobby_list[str(lobby_id)]

    lobby.remove_player(player)

    if len(lobby.players) == 0:
        remove_lobby(lobby_id)
        send_remove_lobby(lobby_id)
    else:
        if player.is_leader():
            lobby.set_new_leader()
        update_lobby(lobby_id)


def get_players_of_lobby(lobby_id):
    lobby = lobby_list[str(lobby_id)]
    return lobby.players


def get_lobby_list_as_array_no_empty_rooms():
    lobby_arr = []
    for key, value in lobby_list.items():
        lobby = value
        if lobby.is_not_empty() and lobby.visibility == 'public' and lobby.is_not_full():
            lobby_arr.append(lobby.to_json())

    return lobby_arr


def get_lobby(lobby_id):
    return lobby_list[str(lobby_id)]
