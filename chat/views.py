from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from chat.models import Dialog
from chat.serializers import MyDialogsSerializer, InitiateDialogSerializer


class MyDialogsView(generics.ListAPIView):
    serializer_class = MyDialogsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Dialog.objects.filter(Q(initiator=self.request.user) | Q(answerer=self.request.user))


class InitiateDialogView(generics.CreateAPIView):
    serializer_class = InitiateDialogSerializer
    permission_classes = (IsAuthenticated,)

# class Messages
