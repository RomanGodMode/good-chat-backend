from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import RegisterUserSerializer, TokenWithUsernameObtainPairSerializer, UserSerializer


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = (AllowAny,)




class TokenWithUsernameObtainPairView(TokenObtainPairView):
    serializer_class = TokenWithUsernameObtainPairSerializer


class ListUnknownUserView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id) \
            .exclude(initiated_dialogs__answerer=self.request.user) \
            .exclude(answered_dialogs__initiator=self.request.user)
