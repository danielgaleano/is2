# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0004_actividadflujo_flujo_pk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='actividadflujo',
            name='flujo_pk',
        ),
    ]
