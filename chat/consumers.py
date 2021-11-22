from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from chat.models import Dialog, DialogMessage
from chat.serializers import DialogMessageSerializer
from chat_backend import settings


class ChatConsumer(JsonWebsocketConsumer):

    def connect(self):
        for dialog in Dialog.objects.filter(Q(initiator=self.scope['user'].id) | Q(answerer=self.scope['user'].id)):
            async_to_sync(self.channel_layer.group_add)(f'dialog-{dialog.id}', self.channel_name)

        self.accept()

    def receive_json(self, content, **kwargs):
        event_type = content.pop('type')

        events: Dict[str, Callable[[dict], None]] = {
            'load_messages': self.load_messages,
            'send_message': self.send_message,
            'delete_message': self.delete_message
        }
        event = events.get(event_type)
        if event:
            event(content)

    # серверные события
    def load_messages(self, data: dict):
        dialog_id = data['dialog']
        page = data['page']

        # TODO: обрабатывать новые сообщения в группе (гига ws перестройка)

        # TODO: проверить сортировку
        # TODO: возможность добавить в группу (ws)
        #

        # TODO: Подумать про батчинг или коуплинг, ну ты понял
        # самое простое что можно сделать это тупа через груп by по sent_at и sender_id

        # TODO: ws middleware который ловит исключения

        messages = DialogMessage.objects.filter(dialog_id=dialog_id)
        paginator = Paginator(messages, settings.CHAT_PAGE_SIZE)

        try:
            messages = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            messages = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            messages = paginator.page(page)

        self.send_json({
            'type': 'loaded_messages',
            'messages': DialogMessageSerializer(messages, many=True).data,
            'page': page,
            'total_pages': paginator.num_pages
        })

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

        async_to_sync(self.channel_layer.group_send)(
            f'dialog-{data["dialog"]}',
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

    def loaded_messages(self, event):
        self.send_json(event)
