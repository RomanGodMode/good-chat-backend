from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import RegisterUserSerializer, TokenWithUsernameObtainPairSerializer, ListUserViewSerializer


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)


class TokenWithUsernameObtainPairView(TokenObtainPairView):
    serializer_class = TokenWithUsernameObtainPairSerializer


class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserViewSerializer
    permission_classes = (IsAuthenticated,)
