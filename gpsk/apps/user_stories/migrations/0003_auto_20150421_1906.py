# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user_stories', '0002_auto_20150421_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='estimacion',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(176)]),
            preserve_default=True,
        ),
    ]
