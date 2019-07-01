from channels.generic.websocket import WebsocketConsumer
import json
from .lobby_list_handler import *
from .models import Card


class LobbyListConsumer(WebsocketConsumer):
    """
    Class of the lobbylist consumer.
    """

    def connect(self):
        """
        User connects to the lobby list route. Name of the channel is "lobbylist".
        """
        self.room_group_name = "lobbylist"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send_lobby_list()

    def send_lobby_list(self):
        """
        Sends all existing lobbies, that are not in a game or empty to the client.
        """
        # Sends LobbyList to Client
        lobbies = get_lobby_list_as_array_no_empty_rooms()
        self.send(text_data=json.dumps({
            "lobbies": lobbies
        }))

    def disconnect(self, close_code):
        """
        Client disconnects from the consumer. Also leaves the channel
        :param close_code: Code for the Issue of disconnecting.
        """
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive update from update lobby in lobby_list_handler
    def update_lobby(self, event):
        """
        Sends the updated lobby to the client when lobby is updated.
        :param event: dict with the message.
        """
        lobby = event['lobby']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'lobby': lobby
        }))

    # Receive update from update lobby in lobby_list_handler
    def remove_lobby(self, event):
        """
        Sends the removed lobby to the client.
        :param event: dict with the message.
        """
        lobby_id = event['lobby_id']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'lobby_id': lobby_id
        }))


class LobbyCreateConsumer(WebsocketConsumer):

    def connect(self):
        """
        Client connects to consumer
        :return:
        """
        self.accept()

    # Receive message from WebSocket
    def receive(self, text_data):
        """
        Checks if the data given are correct. If the data from the client are correct, a lobby is created and the lobby_id
        is sent to the creator.
        :param text_data: Data that are sent by the client.
        """
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
        """
        Client disconnects from the consumer.
        :param close_code: Code for the Issue of disconnecting.
        """
        pass


class LobbyConsumer(WebsocketConsumer):

    def connect(self):
        """
        Client connects to the consumer.
        """
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
        """
        Client sends data to Server. If the data sent contain a name, the user is added to the player. If the data are
        a player id, the player with the id gets kicked. If it is a message. The game is started.
        :param text_data: Data sent by client.
        """
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
        """
        Sends all clients in the lobby that the game is started.
        """
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

    def lobby_full(self, event):
        """
        Sends the user a message when lobby is full.
        :param event: message for player
        :return:
        """
        message = event['message']
        if self.player is None:
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
        """
        User disconnects from lobby. Player is removed from array in lobby.
        :param close_code: Code for the Issue of disconnecting.
        """
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
        """
        Client connects to the consumer.
        """
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
        """
        Gets the data from client.
        If client sends player_id, the player id will be associated to the existing player in the game.
        If card is send, the turn is made.
        If player is send, a card will be drawn for player.
        :param text_data: Client message
        """
        text_data_json = json.loads(text_data)
        key = list(text_data_json.keys())
        try:
            if key[0] == "player_id":
                player_id = text_data_json["player_id"]
                self.player = get_player_of_lobby(self.room_group_name, player_id)
                if self.player is None:
                    self.disconnect(1000)
                else:
                    self.send_initialized_game()

            elif key[0] == "card":
                card = text_data_json["card"]
                card = Card.objects.get(id=card["id"])
                self.play_card_for_player(card)
                if check_if_won_mau_mau(self.room_group_name):
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'send_winner',
                            'player_id': self.player.id
                        }
                    )
            elif key[0] == "player":
                self.draw_card_for_player()
            elif key[0] == "symbol":
                symbol = text_data_json["symbol"]
                self.wish_card_for_player(symbol)
        except IndexError as e:
            print(e)

    def disconnect(self, close_code):
        """
        User disconnects from lobby. Player is removed from game and that is send to the game.
        :param close_code: Code for the Issue of disconnecting.
        """
        remove_player_from_lobby(self.room_group_name, self.player)
        current_player = get_current_player(self.room_group_name)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'player.removed',
                'current_player': current_player.to_json()
            }
        )

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def draw_card_for_player(self):
        """
        Draw a card for a player and sends the card to the player, as well as the next player.
        """
        if self.player is not None:
            cards_before_drawing = self.player.cards.copy()
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

    def wish_card_for_player(self, symbol):
        """
        Wishes a symbol and sends the wished symbol to all clients in game.
        :param symbol: Symbol that is wished.
        """
        if wish_card_in_mau_mau(self.room_group_name, self.player, symbol):
            current_player = get_current_player(self.room_group_name)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'wish_card',
                    'symbol': symbol,
                    'current_player': current_player.to_json()
                }
            )
        else:
            self.send_error_message()

    def wish_card(self, event):
        current_player = event["current_player"]
        symbol = event["symbol"]
        self.send(text_data=json.dumps({
            'current_player': current_player,
            'symbol': symbol
        }))

    def draw_card(self, event):
        player = event["player"]
        cards = event["cards"]
        current_player = event["current_player"]
        remaining_cards = get_card_size_of_mau_mau_game(self.room_group_name)
        if self.player.id == player["id"]:
            self.send(text_data=json.dumps({
                'cards_drawn': cards,
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
        """
        Plays a card for a player and sends the played card to all clients.
        :param card: Card that is played.
        """
        player_card = card
        if self.player is not None:
            if play_card_in_game(self.room_group_name, self.player, player_card):
                current_player = get_current_player(self.room_group_name)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'play_card',
                        'card': player_card.to_json,
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
        if self.player.id == player["id"]:
            cards = self.player.cards
            cards_json = self.cards_to_json(cards)
            self.send(text_data=json.dumps({
                'cards': cards_json,
                'top_card_of_discard_pile': card,
                'current_player': current_player
            }))
        else:
            self.send(text_data=json.dumps({
                'player': player,
                'top_card_of_discard_pile': card,
                'current_player': current_player
            }))

    def send_error_message(self):
        """
        Error message send to client when action is not allowed.
        """
        self.send(text_data=json.dumps({
            'message': 'Nicht gültig!'
        }))

    @staticmethod
    def compare_cards(cards_before_drawing, cards_after_drawing):
        """
        Compares cards of to card arrays.
        :param cards_before_drawing: Card array before client draws.
        :param cards_after_drawing: Card array after client draws.
        :return:
        """
        cards = []
        for card in cards_after_drawing:
            if card not in cards_before_drawing:
                cards.append(card)
        return cards

    @staticmethod
    def cards_to_json(cards):
        """
        Converts cards of a player to a json.
        :param cards: cards that are converted.
        :return: cards as dict.
        """
        # id must be created so the cards key won't be deleted
        cards_json = []

        for card in cards:
            card_json = card.to_json
            cards_json.append(card_json)

        # delete key after getting all cards
        return cards_json

    def sort_player_list(self, players):
        """
        Sorts the player list so that the player of the consumer is at the top.
        :param players: Player list
        :return: Sorted list.
        """
        counter = 0
        index = -1
        for player in players:
            if player.id == self.player.id:
                index = counter
            counter += 1

        sorted_player_list = []

        for i in range(0, len(players)):
            sorted_player_list.append(players[index])

            index += 1
            if index == len(players):
                index = 0

        return sorted_player_list

    def send_initialized_game(self):
        """
        Sends initialized game to the player.
        """
        players = get_players_of_lobby(self.room_group_name)
        players_json = []
        cards_json = []
        players = self.sort_player_list(players)
        for player in players:
            players_json.append(player.to_json())

            if player.id == self.player.id:
                cards = player.cards
                cards_json = self.cards_to_json(cards)

        current_player = get_current_player(self.room_group_name)
        top_discard_card = get_discard_pile_card(self.room_group_name)

        self.send(text_data=json.dumps({
            'players': players_json,
            'cards': cards_json,
            'current_player': current_player.to_json(),
            'remaining_cards': get_card_size_of_mau_mau_game(self.room_group_name),
            'top_card_of_discard_pile': top_discard_card.to_json
        }))

    def send_winner(self, event):
        """
        Sends the winner.
        :param event: Message for client.
        """
        player_id = event["player_id"]
        self.send(text_data=json.dumps({
            'message': "Sieger",
            'player_id': player_id
        }))

    def jack_wish(self, event):
        """
        Send the client that he has to wish a card.
        :param event: Message for client.
        """
        player = event["player"]
        if player["id"] == self.player.id:
            self.send(text_data=json.dumps({
                'message': "Wuensch dir was"
            }))

    def player_removed(self, event):
        """
        Send all clients the current player and the player that left the game.
        :param event: Message for client.
        """
        current_player = event["current_player"]
        players_json = []
        players = get_players_of_lobby(self.room_group_name)

        players_sorted = self.sort_player_list(players)

        for player in players_sorted:
            players_json.append(player.to_json())

        self.send(text_data=json.dumps({
            'players': players_json,
            'current_player': current_player
        }))
