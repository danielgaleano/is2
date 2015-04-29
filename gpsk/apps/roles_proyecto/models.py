from django.db import models
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator

from apps.proyectos.models import Proyecto


class RolProyecto(models.Model):

    class Meta:
        verbose_name = "Rol de Proyecto"
        verbose_name_plural = "Roles de Proyecto"
        default_permissions = ('crear', 'modificar', 'eliminar', 'listar')

    group = models.OneToOneField(Group, null=True)
    es_rol_proyecto = models.BooleanField(default=False)

    def __unicode__(self):
        return self.group.name

    def get_absolute_url(self):
        return reverse('roles_proyecto', kwargs={'pk': self.pk})



class RolProyecto_Proyecto(models.Model):

    class Meta:
        verbose_name = "Rol de Proyecto por Proyecto"
        verbose_name_plural = "Roles de Proyecto por Proyecto"

    user = models.ForeignKey(User, null=True)
    rol_proyecto = models.ForeignKey(RolProyecto)
    proyecto = models.ForeignKey(Proyecto)
    horas_developer = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def __unicode__(self):
        return "%s %s en %s" % (self.user.username, self.rol_proyecto.group.name, self.proyecto.codigo)

    class Meta:
        default_permissions = ()

