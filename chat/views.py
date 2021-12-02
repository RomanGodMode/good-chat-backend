from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import Dialog, ChatGroup
from chat.serializers import MyDialogsSerializer, CreateChatGroupSerializer, InitiateDialogSerializer, ChatGroupSerializer
from chat.services import chat_service


class MyDialogsView(generics.ListAPIView):
    serializer_class = MyDialogsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return chat_service.get_my_dialogs(self.request.user)


class DetailDialogView(generics.RetrieveAPIView):
    serializer_class = MyDialogsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return chat_service.get_my_dialogs(self.request.user)


class InitiateDialogView(generics.CreateAPIView):
    serializer_class = InitiateDialogSerializer
    permission_classes = (IsAuthenticated,)


class CreateChatGroupView(generics.CreateAPIView):
    serializer_class = CreateChatGroupSerializer
    permission_classes = (IsAuthenticated,)


class ChatsListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        chats = chat_service.get_my_chats(self.request.user)
        return Response(chats)


class CreatedGroupsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatGroupSerializer

    def get_queryset(self):
        return self.request.user.created_groups.all()
