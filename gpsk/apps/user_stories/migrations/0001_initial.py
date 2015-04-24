# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flujos', '0001_initial'),
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('descripcion', models.CharField(max_length=40)),
                ('valor_negocio', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('prioridad', models.CharField(default=b'Baja', max_length=15, choices=[(b'Alta', b'Alta'), (b'Media', b'Media'), (b'Baja', b'Baja')])),
                ('valor_tecnico', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('estimacion', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)])),
                ('estado', models.CharField(default=b'No asignado', max_length=15, choices=[(b'No asignado', b'No asignado'), (b'Activo', b'Activo'), (b'Finalizado', b'Finalizado'), (b'Aprobado', b'Aprobado'), (b'Descartado', b'Descartado')])),
                ('flujo', models.ForeignKey(related_name='flujo', to='flujos.Flujo', null=True)),
                ('proyecto', models.ForeignKey(related_name='proyecto_user_story', to='proyectos.Proyecto', null=True)),
                ('usuario', models.ForeignKey(related_name='usuario_user_story', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'default_permissions': ('crear', 'redefinir', 'definir_valor_tecnico_y_estimacion', 'asignar_flujo', 'asignar_sprint', 'asignar_usuario', 'listar', 'consultar_historial', 'aprobar', 'descartar', 'cambiar_estado', 'revertir_cambio_estado', 'definir_horas', 'agregar_nota', 'agregar_archivo'),
            },
            bases=(models.Model,),
        ),
    ]
