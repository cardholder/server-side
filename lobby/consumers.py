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
                send_remove_lobby(self.room_group_name)

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

    def disconnect(self, close_code):
        if self.lobby_id is not None:
            lobby = get_lobby(self.lobby_id)
            if lobby.game is None:
                remove_player_from_lobby(self.lobby_id, self.player)
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


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
            print(player_id)
            self.player = get_player_of_lobby(self.room_group_name, player_id)
            print(self.player)
            if self.player is None:
                self.disconnect(1000)
            else:
                print(self.player.to_json())
                self.send_initialized_game()

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

    def draw_card_for_player(self):
        if self.player is not None:
            cards_before_drawing = self.player.cards
            if draw_card_in_game(self.room_group_name, self.player):
                cards_after_drawing = self.player.cards
                cards = self.compare_cards(cards_before_drawing, cards_after_drawing)
                cards_dict = self.cards_to_json(cards)
                current_player = get_current_player(self.room_group_name)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'draw_card',
                        'cards': cards_dict,
                        'player': self.player.to_json(),
                        'current_player': current_player.to_json()
                    }
                )
            else:
                self.send_error_message()

    def draw_card(self, event):
        player = event["player"]
        cards = event["cards"]
        current_player = event["current_player"]
        remaining_cards = get_card_size_of_mau_mau_game(self.room_group_name)
        if self.player.id == player.id:
            self.send(text_data=json.dumps({
                'cards': cards,
                'remaining_cards': remaining_cards,
                'current_player': current_player
            }))
        else:
            self.send(text_data=json.dumps({
                'player': player,
                'card_amount': len(cards),
                'remaining_cards': remaining_cards,
                'current_player': current_player
            }))

    def play_card_for_player(self, card):
        player_card = Card.objects.get(id=card.id)
        if self.player is not None:
            if play_card_in_game(self.room_group_name, self.player, player_card):
                current_player = get_current_player(self.room_group_name)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'play_card',
                        'card': player_card.to_json(),
                        'player': self.player.to_json(),
                        'current_player': current_player.to_json()
                    }
                )
            else:
                self.send_error_message()

    def play_card(self, event):
        player = event["player"]
        card = event["card"]
        current_player = event["current_player"]
        if self.player.id == player.id:
            self.send(text_data=json.dumps({
                'player': player,
                'card': card,
                'current_player': current_player
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

    @staticmethod
    def cards_to_json(cards):
        # id must be created so the cards key won't be deleted
        cards_dict = {"id": 0, "cards": []}

        for card in cards:
            card_json = card.to_json
            cards_dict["cards"].append(card_json)

        # delete key after getting all cards
        del cards_dict["id"]
        return cards_dict

    def send_initialized_game(self):
        players = get_players_of_lobby(self.room_group_name)
        players_json = []
        cards_json = []
        for player in players:
            players_json.append(player.to_json())

            print("\n\n\n\n\n")
            print(player.id)
            print(self.player.id)
            if player.id == self.player.id:
                cards = player.cards
                cards_json = self.cards_to_json(cards)

        current_player = get_current_player(self.room_group_name)

        self.send(text_data=json.dumps({
            'players': players_json,
            'cards': cards_json,
            'current_player': current_player.to_json(),
            'remaining_cards': get_card_size_of_mau_mau_game(self.room_group_name)
        }))
