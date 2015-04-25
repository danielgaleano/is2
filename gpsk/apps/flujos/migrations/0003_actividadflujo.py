# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flujos', '0002_auto_20150424_1232'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActividadFlujo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=15)),
                ('orden', models.IntegerField(default=0, max_length=10)),
                ('estados', models.ManyToManyField(to='flujos.Estado')),
            ],
            options={
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
    ]
