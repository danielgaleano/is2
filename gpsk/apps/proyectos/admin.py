from django.contrib import admin

from models import Proyecto

from apps.roles_proyecto.models import RolProyecto_Proyecto


admin.site.register(Proyecto)
admin.site.register(RolProyecto_Proyecto)