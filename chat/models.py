from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE


class Dialog(models.Model):
    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'
        unique_together = ('initiator', 'answerer')
        ordering = ('-created_at',)

    initiator = models.ForeignKey(User, verbose_name='Инициатор диалога', on_delete=CASCADE, related_name='initiated_dialogs')
    answerer = models.ForeignKey(User, verbose_name='Отвечающий диалога', on_delete=CASCADE, related_name='answered_dialogs')

    created_at = models.DateTimeField(verbose_name='Момент создания диалога', auto_now_add=True)


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


class DialogMessage(models.Model):
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-sent_at',)

    sender = models.ForeignKey(User, verbose_name='Автор сообщения', on_delete=CASCADE)
    dialog = models.ForeignKey(Dialog, verbose_name='Диалог', on_delete=CASCADE)
    text = models.TextField(verbose_name='Текст сообщения')
    sent_at = models.DateTimeField(verbose_name='Момент отправки сообщения', auto_now_add=True)
