from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterUserView, TokenWithUsernameObtainPairView, ListUnknownUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('login/', TokenWithUsernameObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', ListUnknownUserView.as_view())
]
