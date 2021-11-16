from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat.serializers import DialogMessageSerializer


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self):
        # TODO: коннектить чела только к диалогам которые у него есть
        async_to_sync(self.channel_layer.group_add)('group_name', self.channel_name)
        self.accept()

    def disconnect(self, message):
        async_to_sync(self.channel_layer.group_discard)('group_name', self.channel_name)

    def receive_json(self, content, **kwargs):
        event_type = content.pop('type')

        events: Dict[str, Callable[[dict], None]] = {
            'send_message': self.send_message,
            'delete_message': self.delete_message
        }
        event = events.get(event_type)
        if event:
            event(content)

    # серверные события
    def send_message(self, data: dict):
        data = {
            'sender': self.scope['user'].id,
            'text': data['text'],
            'dialog': data['dialog']
        }
        serializer = DialogMessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = serializer.data
        print(f'{data=}')

        async_to_sync(self.channel_layer.group_send)(
            'group_name',
            {
                'type': 'receive_message',
                'message': message
            }
        )

    def delete_message(self, data: dict):
        print('УДОЛЕНИЕ')

    # клиентские события
    def receive_message(self, event):
        self.send_json(event)
