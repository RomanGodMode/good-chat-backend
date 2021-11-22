from django.contrib.admin import ModelAdmin, register

from chat.models import Dialog, DialogMessage, ChatGroup


@register(Dialog)
class DialogAdmin(ModelAdmin):
    pass


@register(DialogMessage)
class DialogMessageAdmin(ModelAdmin):
    pass


@register(ChatGroup)
class DialogAdmin(ModelAdmin):
    pass
