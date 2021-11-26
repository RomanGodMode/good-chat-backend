from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from chat.models import DialogMessage, GroupMessage, Dialog
from chat.serializers import DialogMessageSerializer, GroupMessageSerializer, InitiateDialogSerializer
from chat.services import chat_service
from chat_backend import settings


class ChatConsumer(JsonWebsocketConsumer):

    def subscribe_for_dialog(self, dialog_id: int, channel_name: str = None):
        group_name = f'dialog-{dialog_id}'
        async_to_sync(self.channel_layer.group_add)(group_name, channel_name if channel_name else self.channel_name)
        self.groups.append(group_name)

    def subscribe_for_group(self, group_id: int):
        group_name = f'group-{group_id}'
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)
        self.groups.append(group_name)

    @property
    def channel_name(self):
        return f'user-{self.scope["user"].id}'

    @channel_name.setter
    def channel_name(self, name):
        pass

    def connect(self):
        for dialog in chat_service.get_my_dialogs(me=self.scope['user']):
            self.subscribe_for_dialog(dialog.id)

        for group in chat_service.get_my_groups(me=self.scope['user']):
            self.subscribe_for_group(group.id)

        self.accept()

    def receive_json(self, content, **kwargs):
        event_type = content.pop('type')

        events: Dict[str, Callable[[dict], None]] = {
            'load_messages': self.load_messages,
            'send_message': self.send_message,
            'delete_message': self.delete_message,
            'subscribe_for_new_dialog': self.subscribe_for_new_dialog,
            'initiate_dialog': self.initiate_dialog
        }
        event = events.get(event_type)
        if event:
            event(content)

    # серверные события
    def load_messages(self, data: dict):
        page = data['page']

        # fixme можно вкинуть только dialog_id | group_id
        dialog_id = data.get('dialog', None)
        group_id = data.get('group', None)

        # TODO: возможность добавить в группу (ws)
        #

        # TODO: Подумать про батчинг или коуплинг, ну ты понял
        # самое простое что можно сделать это тупа через груп by по sent_at и sender_id

        # TODO: ws middleware который ловит исключения

        if dialog_id:
            messages = DialogMessage.objects.filter(dialog_id=dialog_id)
        else:
            messages = GroupMessage.objects.filter(group_id=group_id)

        paginator = Paginator(messages, settings.CHAT_PAGE_SIZE)

        try:
            messages = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            messages = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            messages = paginator.page(page)

        if dialog_id:
            messages = DialogMessageSerializer(messages, many=True).data
        else:
            messages = GroupMessageSerializer(messages, many=True).data

        self.send_json({
            'type': 'loaded_messages',
            'messages': messages,
            'page': page,
            'total_pages': paginator.num_pages
        })

    def send_message(self, data: dict):
        message = {
            'sender': self.scope['user'].id,
            'text': data['text']
        }

        if data.get('dialog'):
            dialog = Dialog.objects.get(id=data['dialog'])
            if not dialog.messages.exists():
                self.subscribe_for_dialog(data['dialog'], f'user-{dialog.answerer.id}')
            serializer = DialogMessageSerializer(data={**message, 'dialog': data['dialog']})
        else:
            serializer = GroupMessageSerializer(data={**message, 'group': data['group']})

        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = serializer.data

        if data.get('dialog'):
            group_name = f'dialog-{message["dialog"]}'
        else:
            group_name = f'group-{message["group"]}'

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                'type': 'receive_message',
                'message': message
            }
        )

    def initiate_dialog(self, data: dict):
        serializer = InitiateDialogSerializer(data=data['dialog'], context={'user': self.scope['user']})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.subscribe_for_dialog(serializer.data['id'])

        self.send_json({
            'type': 'initiate_dialog_success',
            'created_dialog': serializer.data
        })

    def subscribe_for_new_dialog(self, data: dict):
        self.subscribe_for_dialog(data["dialog"])

    def delete_message(self, data: dict):
        print('УДОЛЕНИЕ', data)

    # клиентские события
    def receive_message(self, event):
        self.send_json(event)

    def loaded_messages(self, event):
        self.send_json(event)

    def initiate_dialog_success(self, event):
        self.send_json(event)

    def new_dialog(self, event):
        self.send_json(event)
