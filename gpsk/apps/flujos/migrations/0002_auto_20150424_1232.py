# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flujo',
            name='actividades',
            field=models.ManyToManyField(to='flujos.Actividad', null=True),
            preserve_default=True,
        ),
    ]
