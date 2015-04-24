import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from apps.clientes.models import Cliente


class Proyecto(models.Model):

    ESTADOS_PROYECTO=(
        ('No inciado', 'No inciado'),
        ('Activo', 'Activo'),
        ('Finalizado', 'Finalizado'),
    )
    codigo = models.SlugField(max_length=4, unique=True, null=True)
    nombre_corto = models.CharField(max_length=15)
    nombre_largo = models.CharField(max_length=40)
    fecha_inicio = models.DateField(default=datetime.date.today)
    fecha_fin = models.DateField(default=datetime.date.today)
    cancelado = models.BooleanField(default=False)
    scrum_master = models.ForeignKey(User, null=True, related_name='scrum_master')
    equipo = models.ManyToManyField(User, null=True)
    estado = models.CharField(max_length=15, choices=ESTADOS_PROYECTO, default='No iniciado')
    cliente = models.ForeignKey(Cliente, null=True, related_name='cliente_proyecto')


    def __unicode__(self):
        return self.nombre_corto
    
    def get_absolute_url(self):
        return reverse('proyectos', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear', 'modificar', 'eliminar', 'listar', 'asignar_rol_proyecto')
