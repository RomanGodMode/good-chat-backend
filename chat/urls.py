from django.urls import path

from chat.views import MyDialogsView, CreateChatGroupView, ChatsListView, DetailDialogView, InitiateDialogView

urlpatterns = [
    path('my-dialogs/', MyDialogsView.as_view()),
    path('my-chats/', ChatsListView.as_view()),
    path('dialog/<int:pk>/', DetailDialogView.as_view()),
    path('initiate-dialog/', InitiateDialogView.as_view()),
    path('create-group/', CreateChatGroupView.as_view())
]
