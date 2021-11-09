from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE


class Message(models.Model):
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    user = models.ForeignKey(User, verbose_name='Автор сообщения', on_delete=CASCADE)
    text = models.TextField(verbose_name='Текст сообщения')


class ChatGroup(models.Model):
    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    title = models.CharField(verbose_name='Название группы', max_length=255)
    creator = models.ForeignKey(User, verbose_name='Создатель группы', on_delete=CASCADE)


class ChatGroupMember(models.Model):
    class Meta:
        verbose_name = 'Участник группы'
        verbose_name_plural = 'Участники группы'

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=CASCADE)
    group = models.ForeignKey(ChatGroup, verbose_name='Группа', on_delete=CASCADE)
