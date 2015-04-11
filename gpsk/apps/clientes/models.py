# coding=utf-8
from django.db import models
from django.core.urlresolvers import reverse

class Cliente(models.Model):

    """
    Clase Cliente.
    Crea el perfil del cliente con cada instancia. Se definen los campos nombre, descripción,
    correo electrónico, teléfono y dirección.
    """

    nombre = models.CharField(max_length = 100, verbose_name = 'Nombre', unique = True)
    descripcion = models.CharField(max_length = 300, verbose_name = 'Descripcion')
    correoElectronico = models.EmailField(max_length = 50, verbose_name = 'Email', unique = True)
    telefono = models.CharField(max_length = 20, verbose_name = 'Telefono')
    direccion = models.CharField(max_length = 200, verbose_name = 'Direccion')

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('clientes', kwargs={'pk': self.pk})