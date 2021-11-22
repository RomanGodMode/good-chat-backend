from django.urls import path

from chat.views import MyDialogsView, InitiateDialogView, CreateChatGroupView, ChatsListView

urlpatterns = [
    path('my-dialogs/', MyDialogsView.as_view()),
    path('initiate-dialog/', InitiateDialogView.as_view()),
    path('create-group/', CreateChatGroupView.as_view()),
    path('my-chats/', ChatsListView.as_view())
]
