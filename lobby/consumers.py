# lobby/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .lobby_list_handler import *
from .models import Card


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
        elif key[0] == 'player_id':
            player_id = text_data_json['player_id']
            self.kick_player(player_id)

        elif key[0] == 'message':
            message = text_data_json['message']
            if message == "start":
                start_game(self.lobby_id)
                self.send_start_to_group()

    def disconnect(self, close_code):
        if self.lobby_id is not None:
            remove_player_from_lobby(self.lobby_id, self.player)
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def send_start_to_group(self):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_start',
                'message': "Game is started"
            }
        )

    def send_start(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def kick_player(self, player_id):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_kick',
                'player_id': player_id
            }
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

    def send_kick(self, event):
        player_id = event["player_id"]
        if self.player.id == player_id:
            self.send(text_data=json.dumps({
                'message': "You got kicked!"
            }))


class MauMauConsumer(WebsocketConsumer):

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
        if key[0] == "player_id":
            player_id = text_data_json["player_id"]
            self.player = get_player_of_lobby(self.room_group_name, player_id)
            if self.player is None:
                self.disconnect(1000)

        elif key[0] == "card":
            card = Card.objects.get()
            self.play_card_for_player(card)
        elif key[0] == "player":
            self.draw_card_for_player()

    def disconnect(self, close_code):
        if self.lobby_id is not None:
            remove_player_from_lobby(self.lobby_id, self.player)

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def play_card_for_player(self, card):
        if self.player is not None:
            play_card_in_game(self.room_group_name, self.player, card)

    def draw_card_for_player(self):
        if self.player is not None:
            cards_before_drawing = self.player.cards
            if draw_card_in_game(self.room_group_name, self.player):
                cards_after_drawing = self.player.cards
                cards = self.compare_cards(cards_before_drawing, cards_after_drawing)
                cards_dict = self.cards_to_json(cards)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'draw_card',
                        'cards': cards_dict,
                        'player': self.player.to_json()
                    }
                )
            else:
                self.send_error_message()

    def draw_card(self, event):
        player = event["player"]
        cards = event["cards"]
        remaining_cards = get_card_size_of_mau_mau_game(self.room_group_name)
        if self.player.id == player.id:
            self.send(text_data=json.dumps({
                'cards': cards,
                'remaining_cards': remaining_cards
            }))
        else:
            self.send(text_data=json.dumps({
                'player': player,
                'card_amount': len(cards),
                'remaining_cards': remaining_cards
            }))


    def send_error_message(self):
        self.send(text_data=json.dumps({
            'message': 'Nicht gültig!'
        }))

    def compare_cards(self, cards_before_drawing, cards_after_drawing):
        cards = []
        for card in cards_after_drawing:
            if card not in cards_before_drawing:
                cards.append(card)
        return cards

    def cards_to_json(self, cards):
        cards_dict = {'cards': []}
        for card in cards:
            cards_dict['cards'].append(card.to_json())
        return cards_dict
