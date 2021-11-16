from django.contrib import admin
from django.contrib.admin import ModelAdmin, register

from chat.models import Dialog, DialogMessage


@register(Dialog)
class DialogAdmin(ModelAdmin):
    pass


@register(DialogMessage)
class DialogMessageAdmin(ModelAdmin):
    pass
