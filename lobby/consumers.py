# lobby/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .lobby_list_handler import *


class LobbyListConsumer(WebsocketConsumer):

    def connect(self):
        self.room_group_name = "lobbylist"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send_lobbylist()

    def send_lobbylist(self):
        # Sends LobbyList to Client
        self.send(text_data=json.dumps({
            "lobbies": [
                {
                    "id": "hAsfh8n",
                    "game": "Durak",
                    "visibility": "private",
                    "max_players": 8,
                    "players": [
                        {
                            "id": 0,
                            "name": "PlayerA 1",
                            "role": "leader"
                        },
                        {
                            "id": 1,
                            "name": "PlayerA 2",
                            "role": "player"
                        },
                        {
                            "id": 2,
                            "name": "PlayerA 3",
                            "role": "player"
                        },
                        {
                            "id": 3,
                            "name": "PlayerA 4",
                            "role": "player"
                        }
                    ]
                },
                {
                    "id": "hfgsD23",
                    "game": "Durak",
                    "visibility": "private",
                    "max_players": 8,
                    "players": [
                        {
                            "id": 0,
                            "name": "PlayerB 1",
                            "role": "leader"
                        },
                        {
                            "id": 1,
                            "name": "PlayerB 2",
                            "role": "player"
                        },
                        {
                            "id": 2,
                            "name": "PlayerB 3",
                            "role": "player"
                        },
                        {
                            "id": 3,
                            "name": "PlayerB 4",
                            "role": "player"
                        }
                    ]
                }
            ]
        }))

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
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
        message = text_data_json['message']
        add_player_to_lobby(message["lobby_id"], message["name"])
        players = get_players_of_lobby(message["lobby_id"])

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'players': players
        }))

    def disconnect(self, close_code):
        pass