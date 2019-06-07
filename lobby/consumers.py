# lobby/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .lobby_list_handler import *
from .models import Game


class LobbyListConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = "lobbylist"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send_lobby_list()

    def send_lobby_list(self):
        # Sends LobbyList to Client
        lobbies = get_lobby_list_as_array_no_empty_rooms()
        self.send(text_data=json.dumps({
            "lobbies": lobbies
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive update from update lobby in lobby_list_handler
    def update_lobby(self, event):
        lobby = event['lobby']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'lobby': lobby
        }))

    # Receive update from update lobby in lobby_list_handler
    def remove_lobby(self, event):
        lobby_id = event['lobby_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'lobby_id': lobby_id
        }))


class LobbyCreateConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        game = text_data_json['game']
        visibility = text_data_json['visibility']
        max_players = text_data_json['max_players']
        lobby_id = create_lobby(game, visibility, max_players)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'id': lobby_id
        }))

    def disconnect(self, close_code):
        pass


class LobbyConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs']['room_name']
        self.lobby_id = None
        self.player = None

        if check_if_lobby_exists(self.room_group_name):
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        key = list(text_data_json.keys())
        if key[0] == "name":

            player_name = text_data_json['name']

            if self.lobby_id is None:
                self.lobby_id, self.player = add_player_to_lobby(self.room_group_name, player_name)
                lobby = get_lobby(self.room_group_name)
                if self.lobby_id is not None:
                    self.send_lobby(lobby)
        elif key[0] == "player_id":
            if text_data_json['player_id'] == self.player.id:
                self.send_kick_message()
                self.disconnect(1000)

    def disconnect(self, close_code):
        if self.lobby_id is not None:
            remove_player_from_lobby(self.lobby_id, self.player)
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    def update_lobby(self, event):
        players = event['players']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'players': players
        }))

    # Receive message from room group
    def lobby_full(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
        self.disconnect(1000)

    def send_lobby(self, lobby):
        self.send(text_data=json.dumps({
            'your_id': int(self.player.id),
            'lobby': lobby.to_json()
        }))

    def send_kick_message(self):
        self.send(text_data=json.dumps({
            'message': "You got kicked!"
        }))
