from django.db import models


class Card(models.Model):
    value = models.CharField(max_length=200)
    symbol = models.CharField(max_length=1)

    def __str__(self):
        return str(self.value) + str(self.symbol)

    def to_json(self):
        card_dict = {"id": self.id, "value": self.value, "symbol": self.symbol}
        return card_dict


class CardSet(models.Model):
    name = models.CharField(max_length=200)
    cards = models.ManyToManyField(Card)

    def __str__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=200)
    show_name = models.CharField(max_length=200)
    max_players = models.IntegerField(default=4)
    card_set = models.ForeignKey(CardSet, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
