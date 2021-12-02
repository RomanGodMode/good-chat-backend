# Generated by Django 3.2.9 on 2021-11-29 21:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0012_auto_20211119_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='dialogmessage',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Сообщение прочитано'),
        ),
        migrations.AddField(
            model_name='groupmessage',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Сообщение прочитано'),
        ),
        migrations.AlterField(
            model_name='chatgroup',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_groups', to=settings.AUTH_USER_MODEL, verbose_name='Создатель группы'),
        ),
        migrations.AlterField(
            model_name='dialogmessage',
            name='dialog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.dialog', verbose_name='Диалог'),
        ),
        migrations.AlterField(
            model_name='groupmessage',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatgroup', verbose_name='Группа'),
        ),
        migrations.AlterUniqueTogether(
            name='chatgroupmember',
            unique_together={('user', 'group')},
        ),
    ]
