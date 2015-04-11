# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(unique=True, max_length=100, verbose_name=b'Nombre')),
                ('descripcion', models.CharField(max_length=300, verbose_name=b'Descripcion')),
                ('correoElectronico', models.EmailField(unique=True, max_length=50, verbose_name=b'Email')),
                ('telefono', models.CharField(max_length=20, verbose_name=b'Telefono')),
                ('direccion', models.CharField(max_length=200, verbose_name=b'Direccion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
