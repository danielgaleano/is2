# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_stories', '0003_auto_20150421_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialUserStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operacion', models.CharField(max_length=50)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('user_story', models.ForeignKey(related_name='historial_user_story', to='user_stories.UserStory')),
                ('usuario', models.ForeignKey(related_name='historial_usuario_us', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
