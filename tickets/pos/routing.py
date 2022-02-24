from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/seat_selection/(?P<event_id>\w+)/$', consumers.SeatMapConsumer.as_asgi()),
]