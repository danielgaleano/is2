# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='cliente',
            field=models.ForeignKey(related_name='cliente_proyecto', to='clientes.Cliente', null=True),
            preserve_default=True,
        ),
    ]
