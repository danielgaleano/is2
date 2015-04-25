from django.contrib import admin

from models import Flujo, Actividad, Estado, ActividadFlujo, PlantillaFlujo


# Register your models here.
admin.site.register(Flujo)
admin.site.register(PlantillaFlujo)
admin.site.register(Actividad)
admin.site.register(ActividadFlujo)
admin.site.register(Estado)