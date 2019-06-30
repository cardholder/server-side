from django.db import models


class Card(models.Model):
    """
    Model for cards.

    Has the attributes:
        - value: value of card.
        - symbol: card colour or symbol.
    """
    value = models.CharField(max_length=200)
    symbol = models.CharField(max_length=1)

    def __str__(self):
        return str(self.value) + str(self.symbol)

    @property
    def to_json(self):
        """
        Returns Card as dict.
        :return: card as dict.
        """
        card_dict = {"id": self.id, "value": self.value, "symbol": self.symbol}
        return card_dict


class CardSet(models.Model):
    """
    Model for card set.

    Has the attributes:
        - name: name of card set.
        - cards: cards that are contained in the card set.
    """
    name = models.CharField(max_length=200)
    cards = models.ManyToManyField(Card)

    def __str__(self):
        return self.name


class Game(models.Model):
    """
    Model for games.

    Has the attributes:
       - name: name of the game.
       - show_name: Name that is displayed on the frontend.
       - max_players: Number of players that can play the game.
       - card_set: Card set that is used in the game.
    """
    name = models.CharField(max_length=200)
    show_name = models.CharField(max_length=200)
    max_players = models.IntegerField(default=4)
    card_set = models.ForeignKey(CardSet, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
