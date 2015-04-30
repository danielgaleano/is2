# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('orden', models.IntegerField(default=0, max_length=10)),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActividadFlujo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('orden', models.IntegerField(default=0, max_length=10)),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(default=b'To do', max_length=15)),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flujo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('actividades', models.ManyToManyField(to='flujos.Actividad', null=True)),
                ('proyecto', models.ForeignKey(related_name='proyecto_flujo', to='proyectos.Proyecto', null=True)),
            ],
            options={
                'default_permissions': ('crear', 'modificar', 'eliminar', 'listar'),
            },
            bases=(models.Model,),
        ),
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
        migrations.AddField(
            model_name='actividadflujo',
            name='estados',
            field=models.ManyToManyField(to='flujos.Estado'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actividad',
            name='estados',
            field=models.ManyToManyField(to='flujos.Estado'),
            preserve_default=True,
        ),
    ]
