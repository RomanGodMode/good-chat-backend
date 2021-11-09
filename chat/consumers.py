from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self):
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
        async_to_sync(self.channel_layer.group_send)(
            'group_name',
            {
                'type': 'receive_message',
                'message': {
                    'user_id': 1,
                    'text': data['text']
                }
            }
        )

    def delete_message(self, data: dict):
        print('УДОЛЕНИЕ')

    # клиентские события
    def receive_message(self, event):
        self.send_json(event)

# TODO: добавить jwt-auth
# TODO: личные сообщения
# TODO: добавить сохранение сообщений
