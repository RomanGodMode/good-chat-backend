from django.urls import path

from chat.views import MyDialogsView, InitiateDialogView

urlpatterns = [
    path('my-dialogs/', MyDialogsView.as_view()),
    path('initiate-dialog/', InitiateDialogView.as_view()),
    # path('messages/', )
]
