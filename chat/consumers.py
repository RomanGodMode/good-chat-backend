from typing import Callable, Dict

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, EmptyPage

from chat.chat_consumer_externals import external_groups
from chat.models import DialogMessage, GroupMessage, Dialog, ChatGroup
from chat.paginator import PaginatorWithOffset
from chat.serializers import DialogMessageSerializer, GroupMessageSerializer, AddToChatGroupSerializer
from chat.services import chat_service
from chat_backend import settings


class ChatConsumer(JsonWebsocketConsumer):

    def subscribe_for_dialog(self, dialog_id: int, channel_name: str = None):
        group_name = f'dialog-{dialog_id}'
        async_to_sync(self.channel_layer.group_add)(group_name, channel_name if channel_name else self.channel_name)
        self.groups.append(group_name)

    def subscribe_for_group(self, group_id: int, channel_name: str = None):
        group_name = f'group-{group_id}'
        async_to_sync(self.channel_layer.group_add)(group_name, channel_name if channel_name else self.channel_name)
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

    def disconnect(self, code):
        for external_group in external_groups:
            async_to_sync(self.channel_layer.group_discard)(external_group, self.channel_name)

        super().disconnect(code)

    def receive_json(self, content, **kwargs):
        event_type = content.pop('type')

        events: Dict[str, Callable[[dict], None]] = {
            'load_messages': self.load_messages,
            'send_message': self.send_message,
            'delete_message': self.delete_message,
            'add_to_group': self.add_to_group,
            'mark_as_read': self.mark_as_read,
            'start_typing': self.start_typing,
            'stop_typing': self.stop_typing
        }
        event = events.get(event_type)
        if event:
            try:
                event(content)
            except Exception as e:
                self.send_json({'type': 'error', 'error': e.__dict__})

    # серверные события
    def load_messages(self, data: dict):
        page = data['page']
        shift = data['shift']

        dialog_id = data.get('dialog', None)
        group_id = data.get('group', None)

        if dialog_id:
            messages = DialogMessage.objects.filter(dialog_id=dialog_id)
        else:
            messages = GroupMessage.objects.filter(group_id=group_id)

        paginator = PaginatorWithOffset(messages, settings.CHAT_PAGE_SIZE, shift=shift)

        try:
            paginated_messages = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            paginated_messages = paginator.page(page)
        except EmptyPage:
            page = paginator.num_pages
            paginated_messages = paginator.page(page)

        if dialog_id:
            serialized_messages = DialogMessageSerializer(paginated_messages, many=True).data
        else:
            serialized_messages = GroupMessageSerializer(paginated_messages, many=True).data

        user: User = self.scope['user']

        now_read_messages = messages.exclude(users_that_read=user)
        if now_read_messages.exists():  # если есть хоть одно сообщение не от этого юзера значит
            if dialog_id:
                user.read_dialog_messages.add(*messages)
                user.save()
            else:
                user.read_group_messages.add(*messages)
                user.save()

            if dialog_id:
                group_name = f'dialog-{dialog_id}'
                event = {
                    'type': 'read_messages',
                    'dialog_id': dialog_id,
                    'user_id': user.id
                }
            else:
                group_name = f'group-{group_id}'
                event = {
                    'type': 'read_messages',
                    'group_id': group_id,
                    'user_id': user.id
                }

            async_to_sync(self.channel_layer.group_send)(
                group_name,
                event
            )

        self.send_json({
            'type': 'loaded_messages',
            'messages': serialized_messages,
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

    def add_to_group(self, data: dict):
        serializer = AddToChatGroupSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.subscribe_for_group(data['group'], f'user-{data["user"]}')

        async_to_sync(self.channel_layer.group_send)(
            f'group-{data["group"]}',
            {
                'type': 'added_to_group',
                'group': serializer.data['group'],
                'user_id': data['user']
            }
        )

    def mark_as_read(self, data: dict):
        dialog_id = data.get('dialog_id')
        group_id = data.get('group_id')
        user: User = self.scope['user']

        if dialog_id:
            messages = Dialog.objects.get(id=dialog_id).messages.all()
            user.read_dialog_messages.add(*messages)
            user.save()
        else:
            messages = ChatGroup.objects.get(id=group_id).messages.all()
            user.read_group_messages.add(*messages)
            user.save()

        if dialog_id:
            group_name = f'dialog-{dialog_id}'
            event = {
                'type': 'read_messages',
                'dialog_id': dialog_id,
                'user_id': user.id
            }
        else:
            group_name = f'group-{group_id}'
            event = {
                'type': 'read_messages',
                'group_id': group_id,
                'user_id': user.id
            }

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            event
        )

    def start_typing(self, data: dict):
        dialog_id = data.get('dialog')
        group_id = data.get('group')
        user: User = self.scope['user']

        if dialog_id:
            group_name = f'dialog-{dialog_id}'
            event = {
                'type': 'someone_start_typing',
                'dialog': dialog_id,
                'user': user.id
            }
        else:
            group_name = f'group-{group_id}'
            event = {
                'type': 'someone_start_typing',
                'group': group_id,
                'user': user.id
            }

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            event
        )

    def stop_typing(self, data: dict):
        dialog_id = data.get('dialog')
        group_id = data.get('group')
        user: User = self.scope['user']

        if dialog_id:
            group_name = f'dialog-{dialog_id}'
            event = {
                'type': 'someone_stop_typing',
                'dialog': dialog_id,
                'user': user.id
            }
        else:
            group_name = f'group-{group_id}'
            event = {
                'type': 'someone_stop_typing',
                'group': group_id,
                'user': user.id
            }

        async_to_sync(self.channel_layer.group_send)(
            group_name,
            event
        )

    def delete_message(self, data: dict):
        print('УДОЛЕНИЕ', data)

    # клиентские события
    def receive_message(self, event):
        self.send_json(event)

    def loaded_messages(self, event):
        self.send_json(event)

    def added_to_group(self, event):
        self.send_json(event)

    def read_messages(self, event):
        self.send_json(event)

    def someone_start_typing(self, event):
        self.send_json(event)

    def someone_stop_typing(self, event):
        self.send_json(event)
