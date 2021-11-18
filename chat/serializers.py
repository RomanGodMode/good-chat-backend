from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.exceptions import NotAcceptable
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from chat.models import Dialog, DialogMessage
from users.serializers import UserSerializer


class DialogMessageSerializer(ModelSerializer):
    class Meta:
        model = DialogMessage
        fields = ('sender', 'dialog', 'text', 'id', 'sent_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender'] = UserSerializer(User.objects.get(id=representation['sender'])).data

        return representation


class MyDialogsSerializer(ModelSerializer):
    initiator = UserSerializer(read_only=True)
    answerer = UserSerializer(read_only=True)
    last_message = SerializerMethodField()

    class Meta:
        model = Dialog
        fields = ('id', 'initiator', 'answerer', 'created_at', 'last_message')

    def get_last_message(self, instance):
        return DialogMessageSerializer(DialogMessage.objects.filter(dialog=instance).first()).data


class InitiateDialogSerializer(ModelSerializer):
    initiator = UserSerializer(read_only=True)

    class Meta:
        model = Dialog
        fields = ('answerer', 'id', 'initiator', 'created_at')
        read_only_fields = ('id', 'initiator')

    def create(self, validated_data):
        try:
            validated_data['initiator'] = self.context['request'].user
            return super().create(validated_data)
        except IntegrityError as e:
            message = e.args[0]
            if 'UNIQUE constraint' in message:
                raise NotAcceptable('Диалог уже был создан')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['answerer'] = UserSerializer(User.objects.get(id=representation['answerer'])).data

        return representation
