# This is the handler for the lobby list.
import random
import string
from .lobby import Lobby
from .player import Player
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .maumau import MauMau

lobby_list = {}


def create_lobby(game_name, visibility, max_players):
    # generates a random id for new lobby
    lobby_id = generate_id()
    while check_if_lobby_exists(lobby_id):
        # generates a new lobby_id if it already exists
        lobby_id = generate_id()

    lobby = Lobby(lobby_id, game_name, visibility, max_players)
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
    if lobby.visibility == "public":
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
        {"type": "lobby.full", "message": "Lobby is full!"},
    )


def add_player_to_lobby(lobby_id, name):
    lobby = lobby_list[str(lobby_id)]

    if not lobby.is_not_full():
        send_lobby_is_full(lobby_id)
        return None, None

    player_id = lobby.get_highest_player_id_of_lobby()
    player_id = player_id + 1
    if player_id == 0:
        role = "leader"
    else:
        role = "player"

    player = Player(player_id, name, role)
    lobby.add_player(player)
    update_lobby(lobby_id)

    if not lobby.is_not_full():
        send_remove_lobby(lobby_id)

    return lobby_id, player


def remove_player_from_lobby(lobby_id, player):
    lobby = lobby_list[str(lobby_id)]

    lobby.remove_player(player)
    if lobby.game is not None:
        if isinstance(lobby.game, MauMau):
            lobby.game.remove_player_from_game(player)

    if len(lobby.players) == 0:
        remove_lobby(lobby_id)
        send_remove_lobby(lobby_id)
    else:
        if lobby.game is None:
            if player.is_leader():
                lobby.set_new_leader()
            update_lobby(lobby_id)


def get_lobby_list_as_array_no_empty_rooms():
    lobby_arr = []
    for key, value in lobby_list.items():
        lobby = value
        if lobby.is_not_empty() and lobby.visibility == 'public' and lobby.is_not_full() and lobby.game is None:
            lobby_arr.append(lobby.to_json())

    return lobby_arr


def get_lobby(lobby_id):
    return lobby_list[str(lobby_id)]


def get_player_of_lobby(lobby_id, player_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        for player in lobby.players:
            if player.id == player_id:
                return player
    return None


def start_game(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if lobby.game_name == "Mau Mau":
            lobby.game = MauMau(lobby_id, lobby.players)


def play_card_in_game(lobby_id, player, card):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            return lobby.game.play_card(player, card)
    return False


def draw_card_in_game(lobby_id, player):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            if player == lobby.game.current_player:
                return lobby.game.draw_cards(player)
    return False


def get_card_size_of_mau_mau_game(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            return len(lobby.game.cards)


def get_current_player(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            return lobby.game.current_player


def get_players_of_lobby(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        players = []
        for player in lobby.players:
            players.append(player)
        return players


def get_discard_pile_card(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            discard_card = lobby.game.get_top_discard_card()
            return discard_card


def check_if_won_mau_mau(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            return lobby.game.won_game()


def wish_card_in_mau_mau(lobby_id, player, symbol):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        if isinstance(lobby.game, MauMau):
            return lobby.game.make_card_wish(symbol, player)


def get_players_of_lobby_as_json(lobby_id):
    if check_if_lobby_exists(lobby_id):
        lobby = lobby_list[str(lobby_id)]
        return lobby.players_to_json()
