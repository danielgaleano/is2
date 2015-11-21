import datetime
import os

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from apps.flujos.models import Flujo, Actividad, Estado
from apps.proyectos.models import Proyecto
from apps.sprints.models import Sprint


class UserStory(models.Model):
    """
    Clase User Story.
    Crea el formulario para los User Stories para cada instancia de la user story,
    el cual define los campos nombre, descripcion,valor del negocio, prioridad,
    valor tecnico, estimacion, usuario, estado, flujo, proyecto y sprint.
    """

    ESTADO_USER_STORY=(
        ('No asignado', 'No asignado'),
        ('Activo', 'Activo'),
        ('Pendiente', 'Pendiente'),
        ('Finalizado', 'Finalizado'),
        ('Aprobado', 'Aprobado'),
        ('Descartado', 'Descartado'),
    )
    nombre = models.CharField(max_length=15)
    descripcion = models.CharField(max_length=140)
    valor_negocio = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    prioridad = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    valor_tecnico = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    estimacion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(240)], default=0)
    usuario = models.ForeignKey(User, null=True, related_name='usuario_user_story')
    estado = models.CharField(max_length=15, choices=ESTADO_USER_STORY, default='No asignado')
    flujo = models.ForeignKey(Flujo, null=True, related_name='flujo')
    proyecto = models.ForeignKey(Proyecto, null=True, related_name='proyecto_user_story')
    sprint = models.ForeignKey(Sprint, null=True, related_name='sprint_user_story')
    horas_acumuladas = models.IntegerField(validators=[MinValueValidator(0)], default=0)

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('user_stories', kwargs={'pk': self.pk})

    class Meta:
        default_permissions = ('crear',
                               'redefinir',
                               'definir_valor_tecnico_y_estimacion',
                               'asignar_flujo',
                               'asignar_sprint',
                               'asignar_usuario',
                               'listar',
                               'consultar_historial',
                               'aprobar',
                               'descartar',
                               'cambiar_estado',
                               'revertir_cambio_estado',
                               'definir_horas',
                               'agregar_nota',
                               'agregar_archivo')


class HistorialUserStory(models.Model):
    user_story = models.ForeignKey(UserStory, related_name='historial_user_story')
    operacion = models.CharField(max_length=50)
    campo = models.CharField(max_length=25, default="")
    valor = models.CharField(max_length=40, default="")
    usuario = models.ForeignKey(User, related_name='historial_usuario_us')
    fecha = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s a %s por el usuario %s el %s" % (self.user_story.nombre, self.operacion, self.campo, self.valor,
                                               self.usuario.username, self.fecha.strftime('%d-%m-%Y %H:%M:%S'))


class UserStoryDetalle(models.Model):
    user_story = models.OneToOneField(UserStory)
    actividad = models.ForeignKey(Actividad, related_name='actividad_us')
    estado = models.ForeignKey(Estado, related_name='estado_us')

    def __unicode__(self):
        return self.user_story.nombre

    class Meta:
        default_permissions = ()


class Tarea(models.Model):
    TIPO_TAREA = (
        ('Registro de Tarea', 'Registro de Tarea'),
        ('Cambio de Estado', 'Cambio de Estado'),
    )
    user_story = models.ForeignKey(UserStory, related_name='user_story_tarea')
    descripcion = models.TextField(max_length=140)
    horas_de_trabajo = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(240)], default=0)
    actividad = models.ForeignKey(Actividad, related_name='actividad_tarea')
    estado = models.ForeignKey(Estado, related_name='estado_tarea')
    sprint = models.ForeignKey(Sprint, related_name='sprint_tarea')
    flujo = models.ForeignKey(Flujo, related_name='flujo_tarea')
    fecha = models.DateTimeField(auto_now_add=True, default=datetime.date.today)
    tipo = models.CharField(max_length=25, choices=TIPO_TAREA, default='Cambio de Estado')
    usuario = models.ForeignKey(User, related_name='user_tarea', default=1)

    def __unicode__(self):
        return "%s %s en %s - %s - %s - %s el %s" % ("Tarea en ", self.user_story.nombre, self.sprint,
                                                    self.flujo, self.actividad, self.estado,
                                                    self.fecha)

    class Meta:
        default_permissions = ()


class Archivo(models.Model):
    user_story = models.ForeignKey(UserStory, related_name='user_story_archivo')
    archivo = models.FileField(upload_to='user-stories')

    def filename(self):
        return os.path.basename(self.archivo.name)

    def __unicode__(self):
        return "Archivo - %s - %s" % (self.user_story.nombre, datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

    class Meta:
        default_permissions = ()


class Nota(models.Model):
    texto = models.TextField(max_length=140)
    user_story = models.ForeignKey(UserStory, related_name='user_story_nota')
    fecha = models.DateTimeField(auto_now_add=True, default=datetime.date.today)
    usuario = models.ForeignKey(User, related_name='user_nota', default=1)

    def __unicode__(self):
        return "%s %s el %s por %s" % ("Nota en ", self.user_story.nombre, self.fecha, self.usuario.username)

    class Meta:
        default_permissions = ()


class AdjuntoFileModel(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)

    class Meta:
        default_permissions = ()


class Adjunto(models.Model):
    user_story = models.ForeignKey(UserStory, related_name='user_story_adjunto')
    archivo = models.FileField(upload_to='user_stories.AdjuntoFileModel/bytes/filename/mimetype', blank=True, null=True)

    def __unicode__(self):
        return "Archivo - %s - %s" % (self.user_story.nombre, datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))

    class Meta:
        default_permissions = ()