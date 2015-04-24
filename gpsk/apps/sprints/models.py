from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from apps.flujos.models import Flujo
from apps.proyectos.models import Proyecto


class Sprint(models.Model):

    ESTADO_SPRINT = (
        ('No iniciado', 'No iniciado'),
        ('Activo', 'Activo'),
        ('Finalizado', 'Finalizado'),
    )
    nombre = models.CharField(max_length=15)
    duracion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(30)], default=0)
    estado = models.CharField(max_length=15, choices=ESTADO_SPRINT, default='No iniciado')
    flujos = models.ManyToManyField(Flujo, null=True)
    proyecto = models.ForeignKey(Proyecto, null=True, related_name='proyecto_sprint')

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('sprints', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear',
                               'modificar',
                               'listar',
                               'iniciar',
                               'finalizar',
                               'asignar_flujo')
