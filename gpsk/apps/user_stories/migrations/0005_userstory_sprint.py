# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sprints', '0001_initial'),
        ('user_stories', '0004_historialuserstory'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='sprint',
            field=models.ForeignKey(related_name='sprint_user_story', to='sprints.Sprint', null=True),
            preserve_default=True,
        ),
    ]
