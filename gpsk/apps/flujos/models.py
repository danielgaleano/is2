from django.db import models


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


class Flujo(models.Model):
    nombre = models.CharField(max_length=15)
    actividades = models.ManyToManyField(Actividad)
    


    def __unicode__(self):
        return self.nombre
    
    def get_absolute_url(self):
        return reverse('flujos', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear', 'modificar', 'eliminar', 'listar')

