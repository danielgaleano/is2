# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0001_initial'),
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('duracion', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)])),
                ('estado', models.CharField(default=b'No iniciado', max_length=15, choices=[(b'No iniciado', b'No iniciado'), (b'Activo', b'Activo'), (b'Finalizado', b'Finalizado')])),
                ('flujos', models.ManyToManyField(to='flujos.Flujo', null=True)),
                ('proyecto', models.ForeignKey(related_name='proyecto_sprint', to='proyectos.Proyecto', null=True)),
            ],
            options={
                'default_permissions': ('crear', 'modificar', 'listar', 'iniciar', 'finalizar', 'asignar_flujo'),
            },
            bases=(models.Model,),
        ),
    ]
