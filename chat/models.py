from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
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
        unique_together = ('title', 'creator')

    title = models.CharField(verbose_name='Название группы', validators=[MinLengthValidator(3)], max_length=50)
    creator = models.ForeignKey(User, verbose_name='Создатель группы', on_delete=CASCADE, related_name='created_groups')

    members = models.ManyToManyField(User, verbose_name='Участники группы', through='ChatGroupMember', related_name='chat_groups')
    created_at = models.DateTimeField(verbose_name='Момент создания группы', auto_now_add=True)


class ChatGroupMember(models.Model):
    class Meta:
        verbose_name = 'Участник группы'
        verbose_name_plural = 'Участники группы'
        unique_together = ('user', 'group')

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=CASCADE)
    group = models.ForeignKey(ChatGroup, verbose_name='Группа', on_delete=CASCADE)
    joined_at = models.DateTimeField(verbose_name='Момент присоединения к группе', auto_now_add=True)


class AbstractMessage(models.Model):
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-sent_at',)
        abstract = True

    sender = models.ForeignKey(User, verbose_name='Автор сообщения', on_delete=CASCADE)
    text = models.TextField(verbose_name='Текст сообщения')
    sent_at = models.DateTimeField(verbose_name='Момент отправки сообщения', auto_now_add=True)


class DialogMessage(AbstractMessage):
    class Meta(AbstractMessage.Meta):
        verbose_name = 'Сообщение диалогов'
        verbose_name_plural = 'Сообщения диалогов'

    dialog = models.ForeignKey(Dialog, verbose_name='Диалог', on_delete=CASCADE, related_name='messages')
    users_that_read = models.ManyToManyField(User, verbose_name='Пользователи прочитавшие сообщение', related_name='read_dialog_messages')


class GroupMessage(AbstractMessage):
    class Meta(AbstractMessage.Meta):
        verbose_name = 'Сообщение групп'
        verbose_name_plural = 'Сообщения групп'

    group = models.ForeignKey(ChatGroup, verbose_name='Группа', on_delete=CASCADE, related_name='messages')
    users_that_read = models.ManyToManyField(User, verbose_name='Пользователи прочитавшие сообщение', related_name='read_group_messages')
