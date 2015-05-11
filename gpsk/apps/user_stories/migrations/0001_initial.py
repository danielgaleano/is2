# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sprints', '0001_initial'),
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistorialUserStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operacion', models.CharField(max_length=50)),
                ('campo', models.CharField(default=b'', max_length=25)),
                ('valor', models.CharField(default=b'', max_length=40)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.TextField(max_length=140)),
                ('horas_de_trabajo', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(240)])),
                ('fecha', models.DateTimeField(default=datetime.date.today, auto_now_add=True)),
                ('actividad', models.ForeignKey(related_name='actividad_tarea', to='flujos.Actividad')),
                ('estado', models.ForeignKey(related_name='estado_tarea', to='flujos.Estado')),
                ('flujo', models.ForeignKey(related_name='flujo_tarea', to='flujos.Flujo')),
                ('sprint', models.ForeignKey(related_name='sprint_tarea', to='sprints.Sprint')),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('descripcion', models.CharField(max_length=40)),
                ('valor_negocio', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('prioridad', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('valor_tecnico', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('estimacion', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(240)])),
                ('estado', models.CharField(default=b'No asignado', max_length=15, choices=[(b'No asignado', b'No asignado'), (b'Activo', b'Activo'), (b'Pendiente', b'Pendiente'), (b'Finalizado', b'Finalizado'), (b'Aprobado', b'Aprobado'), (b'Descartado', b'Descartado')])),
                ('flujo', models.ForeignKey(related_name='flujo', to='flujos.Flujo', null=True)),
                ('proyecto', models.ForeignKey(related_name='proyecto_user_story', to='proyectos.Proyecto', null=True)),
                ('sprint', models.ForeignKey(related_name='sprint_user_story', to='sprints.Sprint', null=True)),
                ('usuario', models.ForeignKey(related_name='usuario_user_story', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'default_permissions': ('crear', 'redefinir', 'definir_valor_tecnico_y_estimacion', 'asignar_flujo', 'asignar_sprint', 'asignar_usuario', 'listar', 'consultar_historial', 'aprobar', 'descartar', 'cambiar_estado', 'revertir_cambio_estado', 'definir_horas', 'agregar_nota', 'agregar_archivo'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserStoryDetalle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actividad', models.ForeignKey(related_name='actividad_us', to='flujos.Actividad')),
                ('estado', models.ForeignKey(related_name='estado_us', to='flujos.Estado')),
                ('user_story', models.OneToOneField(to='user_stories.UserStory')),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tarea',
            name='user_story',
            field=models.ForeignKey(related_name='user_story_tarea', to='user_stories.UserStory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historialuserstory',
            name='user_story',
            field=models.ForeignKey(related_name='historial_user_story', to='user_stories.UserStory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historialuserstory',
            name='usuario',
            field=models.ForeignKey(related_name='historial_usuario_us', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
