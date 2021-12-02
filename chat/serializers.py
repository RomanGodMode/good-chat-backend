from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.exceptions import NotAcceptable
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from chat.chat_consumer_externals import subscribe_for_dialog
from chat.models import Dialog, DialogMessage, ChatGroup, GroupMessage, ChatGroupMember
from users.mixins import GetUserSerializerMixin
from users.serializers import UserSerializer


class InitiateDialogSerializer(ModelSerializer, GetUserSerializerMixin):
    initiator = UserSerializer(read_only=True)

    class Meta:
        model = Dialog
        fields = ('answerer', 'id', 'initiator', 'created_at')
        read_only_fields = ('id', 'initiator')

    def create(self, validated_data):
        try:
            request = self.context.get('request', None)
            validated_data['initiator'] = request.user if request else self.context['user']

            already_created_dialog = Dialog.objects.filter(answerer=self.get_user(), initiator_id=validated_data['answerer']).first()
            if already_created_dialog:
                subscribe_for_dialog(
                    dialog_id=already_created_dialog.id,
                    channel_name=f'user-{self.get_user().id}'
                )
                return already_created_dialog

            instance = Dialog.objects.create(**validated_data)
            subscribe_for_dialog(
                dialog_id=instance.id,
                channel_name=f'user-{self.get_user().id}'
            )
            return instance

        except IntegrityError as e:
            message = e.args[0]
            if 'UNIQUE constraint' in message:
                raise NotAcceptable('That dialog has already been created')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['answerer'] = UserSerializer(User.objects.get(id=representation['answerer'])).data

        return representation


class CreateChatGroupSerializer(ModelSerializer, GetUserSerializerMixin):
    class Meta:
        model = ChatGroup
        fields = ('id', 'title', 'creator', 'members', 'created_at')
        read_only_fields = ('id', 'creator', 'members')

    def save(self, **kwargs):
        try:
            return super().save(**kwargs, creator=self.get_user(), members=[self.get_user()])
        except IntegrityError as e:
            message = e.args[0]
            if 'UNIQUE constraint' in message:
                raise NotAcceptable('Group with this name has already been created')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['creator'] = UserSerializer(User.objects.get(id=representation['creator'])).data
        representation['members'] = UserSerializer(User.objects.filter(id__in=representation['members']), many=True).data

        return representation


class AddToChatGroupSerializer(ModelSerializer):
    class Meta:
        model = ChatGroupMember
        fields = ('user', 'group', 'joined_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['group'] = ChatGroupSerializer(ChatGroup.objects.get(id=representation['group'])).data

        return representation


class DialogMessageSerializer(ModelSerializer):
    class Meta:
        model = DialogMessage
        fields = ('sender', 'dialog', 'text', 'id', 'sent_at', 'users_that_read')
        read_only_fields = ('users_that_read',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['sender'] = UserSerializer(User.objects.get(id=representation['sender'])).data

        return representation


class GroupMessageSerializer(ModelSerializer):
    class Meta:
        model = GroupMessage
        fields = ('sender', 'group', 'text', 'id', 'sent_at', 'users_that_read')
        read_only_fields = ('users_that_read',)

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
        last_message = instance.messages.first()
        if last_message is None:
            return None
        return DialogMessageSerializer(last_message).data


class ChatGroupSerializer(ModelSerializer):
    members = UserSerializer(read_only=True, many=True)
    creator = UserSerializer(read_only=True)
    last_message = SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = ('id', 'title', 'members', 'creator', 'created_at', 'last_message')

    def get_last_message(self, instance):
        last_message = instance.messages.first()
        if last_message is None:
            return None
        return GroupMessageSerializer(last_message).data
