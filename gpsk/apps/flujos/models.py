from django.db import models
from django.core.urlresolvers import reverse

from apps.proyectos.models import Proyecto


class Estado(models.Model):
    nombre = models.CharField(max_length=15, default="To do")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __unicode__(self):
        return self.nombre
    
    class Meta:
        default_permissions = ()


class Actividad(models.Model):
    nombre = models.CharField(max_length=15)
    estados = models.ManyToManyField(Estado)
    orden = models.IntegerField(max_length=10, default=0)


    def __unicode__(self):
        return self.nombre
    
    class Meta:
        default_permissions = ()


class ActividadFlujo(models.Model):
    nombre = models.CharField(max_length=15)
    estados = models.ManyToManyField(Estado)
    orden = models.IntegerField(max_length=10, default=0)

    def __unicode__(self):
        return self.nombre

    class Meta:
        default_permissions = ()


class PlantillaFlujo(models.Model):
    nombre = models.CharField(max_length=15)
    actividades = models.ManyToManyField(ActividadFlujo, null=True)

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('flujos', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear', 'modificar', 'eliminar', 'listar')


class Flujo(models.Model):
    nombre = models.CharField(max_length=15)
    actividades = models.ManyToManyField(Actividad, null=True)
    proyecto = models.ForeignKey(Proyecto, null=True, related_name='proyecto_flujo')
    


    def __unicode__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('flujos', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear', 'modificar', 'eliminar', 'listar')

