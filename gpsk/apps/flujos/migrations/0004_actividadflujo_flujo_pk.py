# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0003_actividadflujo'),
    ]

    operations = [
        migrations.AddField(
            model_name='actividadflujo',
            name='flujo_pk',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
