# chat/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r"^lobbylist/$", consumers.LobbyListConsumer),
    url(r"^create/$", consumers.LobbyCreateConsumer),
    url(r"^lobby/(?P<room_name>[^/]+)/$", consumers.LobbyConsumer),
]