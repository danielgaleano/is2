# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0005_remove_actividadflujo_flujo_pk'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlantillaFlujo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('actividades', models.ManyToManyField(to='flujos.ActividadFlujo', null=True)),
            ],
            options={
                'default_permissions': ('crear', 'modificar', 'eliminar', 'listar'),
            },
            bases=(models.Model,),
        ),
    ]
