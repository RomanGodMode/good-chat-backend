from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.serializers import MyDialogsSerializer, InitiateDialogSerializer, CreateChatGroupSerializer, ChatGroupSerializer
from chat.services import chat_service


class MyDialogsView(generics.ListAPIView):
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
