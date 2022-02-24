import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


from .models import Event, Seat, PreReservation

class SeatMapConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['event_id']
        self.room_group_name = 'event_%s' % self.room_name
        self.user = self.scope["user"]
        self.event = await database_sync_to_async(Event.objects.filter(id=self.room_name).first)()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        seat_code = text_data_json['seat_code']
        action = text_data_json['action']

        if action == "select":
            status = await self.is_prerreserved(seat_code)
            print(status)
            if status == "Free":
                print("Vamos a reservar el asiento")
                await self.book_seat(seat_code)
                await self.send(text_data=json.dumps({
                    'action': "select",
                    'seat_code': seat_code
                }))
                others_action = "block"
            
        elif action == "unselect":
            await self.free_seat(seat_code)
            others_action = "unblock"
            await self.send(text_data=json.dumps({
                    'action': "unblock",
                    'seat_code': seat_code
                }))
            pass

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'seat_selected',
                'seat_code': seat_code,
                'channel_name': self.channel_name,
                'action' : others_action
            }
        )

    async def seat_selected(self, event):
        seat_code = event['seat_code']
        action = event['action']
        if event['channel_name'] != self.channel_name:
            await self.send(text_data= json.dumps({
                'seat_code' : seat_code,
                'action' : action
            }))

    @database_sync_to_async
    def is_prerreserved(self,seat_code):
        seat_row = int(seat_code[1:3])
        seat_col = int(seat_code[4:])
        p = PreReservation.objects.filter(event = self.event, seat__venue = self.event.venue, seat__row = seat_row, seat__column = seat_col)
        if p.exists():
            p1 = p.first()
            if p1.user == self.user:
                if p1.session_id == self.scope['session'].session_key:
                    return "Yours"
                else:
                    return "Blocked"
            else:
                return "Blocked"
        else:
            s = Seat.objects.filter(row = seat_row, column = seat_col, venue = self.event.venue).first()
            if s.is_occupied(self.event):
                return "Blocked"
            else:
                return "Free"

    @database_sync_to_async
    def book_seat(self, seat_code):
        seat_row = int(seat_code[1:3])
        seat_col = int(seat_code[4:])
        s = Seat.objects.filter(row=seat_row, column=seat_col, venue = self.event.venue).first()
        p = PreReservation()
        p.seat = s
        p.event = self.event
        p.user = self.user
        p.session_id = self.scope['session'].session_key
        p.save()

    @database_sync_to_async
    def free_seat(self, seat_code):
        seat_row = int(seat_code[1:3])
        seat_col = int(seat_code[4:])
        PreReservation.objects.filter(seat__row = seat_row, seat__column = seat_col, seat__venue = self.event.venue, event = self.event, user=self.user, session_id = self.scope['session'].session_key ).delete()