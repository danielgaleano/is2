# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0002_proyecto_cliente'),
        ('flujos', '0006_plantillaflujo'),
    ]

    operations = [
        migrations.AddField(
            model_name='flujo',
            name='proyecto',
            field=models.ForeignKey(related_name='proyecto_flujo', to='proyectos.Proyecto', null=True),
            preserve_default=True,
        ),
    ]
