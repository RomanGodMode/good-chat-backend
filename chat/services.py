from datetime import datetime
from itertools import chain
from operator import attrgetter
from time import strptime
from typing import Union

from django.contrib.auth.models import User
from django.db.models import Q, Exists

from chat.functions import opt
from chat.models import Dialog, ChatGroup, DialogMessage
from chat.serializers import MyDialogsSerializer, ChatGroupSerializer
from chat_backend import settings


def parse_moment(s: str):
    return strptime(s, settings.REST_FRAMEWORK['DATETIME_FORMAT'])


class ChatService:

    def get_my_dialogs(self, me: User):
        return Dialog.objects.filter(Q(initiator=me) | Q(answerer=me) & Exists(DialogMessage.objects.all()))

    def get_my_groups(self, me: User):
        return me.chat_groups.all()

    def get_my_chats(self, me: User):
        def chat_sort_key(chat):
            last_message_sent_moment = opt(chat, 'last_message.sent_at')
            if last_message_sent_moment:
                return max(parse_moment(chat['created_at']), parse_moment(last_message_sent_moment))
            return parse_moment(chat['created_at'])

        return sorted(
            chain(
                MyDialogsSerializer(self.get_my_dialogs(me), many=True).data,
                ChatGroupSerializer(self.get_my_groups(me), many=True).data
            ),
            key=chat_sort_key,
            reverse=True
        )


chat_service = ChatService()
