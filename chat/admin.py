from django.contrib.admin import ModelAdmin, register

from chat.models import Dialog, DialogMessage, ChatGroup, ChatGroupMember


@register(Dialog)
class DialogAdmin(ModelAdmin):
    pass


@register(DialogMessage)
class DialogMessageAdmin(ModelAdmin):
    pass


@register(ChatGroup)
class DialogAdmin(ModelAdmin):
    pass


@register(ChatGroupMember)
class DialogAdmin(ModelAdmin):
    pass


