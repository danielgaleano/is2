# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='descripcion',
            field=models.CharField(max_length=300, verbose_name=b'Descripcion'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='cliente',
            name='direccion',
            field=models.CharField(max_length=200, verbose_name=b'Direccion'),
            preserve_default=True,
        ),
    ]
