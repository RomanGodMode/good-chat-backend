from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


class RegisterUserSerializer(ModelSerializer):
    password = serializers.CharField(min_length=4, max_length=12, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        read_only_fields = ('id',)
        write_only_fields = ('password',)
