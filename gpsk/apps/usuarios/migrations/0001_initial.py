# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('roles_proyecto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('telefono', models.CharField(max_length=20)),
                ('direccion', models.CharField(max_length=50)),
                ('rolesproyecto', models.ManyToManyField(to='roles_proyecto.RolProyecto', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('crear', 'modificar', 'activar', 'inactivar', 'listar'),
            },
            bases=(models.Model,),
        ),
    ]
