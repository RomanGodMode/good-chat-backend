from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterUserSerializer(ModelSerializer):
    password = serializers.CharField(min_length=4, max_length=12, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        read_only_fields = ('id',)
        write_only_fields = ('password',)


class TokenWithUsernameObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        print(f'{user=}')
        token['name'] = user.username
        return token


class ListUserViewSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
