# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codigo', models.SlugField(max_length=4, unique=True, null=True)),
                ('nombre_corto', models.CharField(max_length=15)),
                ('nombre_largo', models.CharField(max_length=40)),
                ('fecha_inicio', models.DateField(default=datetime.date.today)),
                ('fecha_fin', models.DateField(default=datetime.date.today)),
                ('cancelado', models.BooleanField(default=False)),
                ('estado', models.CharField(default=b'No iniciado', max_length=15, choices=[(b'No inciado', b'No inciado'), (b'Activo', b'Activo'), (b'Finalizado', b'Finalizado')])),
                ('equipo', models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True)),
                ('scrum_master', models.ForeignKey(related_name='scrum_master', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'default_permissions': ('crear', 'modificar', 'eliminar', 'listar', 'asignar_rol_proyecto'),
            },
            bases=(models.Model,),
        ),
    ]
