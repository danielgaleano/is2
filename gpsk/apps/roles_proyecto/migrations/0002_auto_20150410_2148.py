# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles_proyecto', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rolproyecto',
            options={'default_permissions': ('crear', 'modificar', 'eliminar', 'listar'), 'verbose_name': 'Rol de Proyecto', 'verbose_name_plural': 'Roles de Proyecto'},
        ),
    ]
