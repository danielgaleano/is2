from operator import attrgetter
import urlparse
import json
import locale
import datetime

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.views import generic
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from models import Sprint
from forms import SprintCreateForm, SprintUpdateForm, SprintAsignarUserStoryForm, SprintUpdateUserStoryForm, \
    RegistrarTareaForm, AdjuntarArchivoForm, AgregarNotaForm, AgregarAdjuntoForm
from apps.proyectos.models import Proyecto
from apps.proyectos.views import habiles
from apps.user_stories.models import UserStory, HistorialUserStory, UserStoryDetalle, Tarea, Archivo, Nota, Adjunto
from apps.roles_proyecto.models import RolProyecto_Proyecto, RolProyecto
from apps.flujos.models import Flujo
from tasks import cambio_estado, fin_user_story, reversion_estado, aprobacion_user_story


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de sprints en el Index
    de la aplicacion sprints.

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    template_name = 'sprints/index.html'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])

        return Sprint.objects.filter(proyecto=self.proyecto).order_by('pk')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        lista_sprints = Sprint.objects.filter(proyecto=self.proyecto).order_by('pk')

        hay_activo = False
        for sprint in lista_sprints:
            if sprint.estado == 'Activo':
                hay_activo = True

        context['hay_activo'] = hay_activo
        context['proyecto'] = self.proyecto

        return context


class SprintCreate(UpdateView):
    """
    Clase que despliega el formulario para la creacion de sprints.

    @ivar form_class: Formulario que se utiliza para la creacion de sprints
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = SprintCreateForm
    template_name = 'sprints/create.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que obtiene los datos del usuario a ser modificado.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @type queryset: django.db.models.query
        @param queryset: Consulta a la base de datos

        @rtype: Sprint
        @return: Sprint actual a ser modificado
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de sprints una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('sprints:index', args=[obj.pk])

    def get_form_kwargs(self):
        """
        Metodo que inserta los formularios con los argumentos clave.
        """
        kwargs = super(SprintCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SprintUpdate(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de sprints.

    @ivar form_class: Formulario que se utiliza para la modficacion de sprints
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = SprintUpdateForm
    template_name = 'sprints/update.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que obtiene los datos del sprint a ser modificado.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @type queryset: django.db.models.query
        @param queryset: Consulta a la base de datos

        @rtype: Sprint
        @return: Sprint a ser modificado
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de sprints una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion sprints
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('sprints:index', args=[obj.pk])

    def get_initial(self):
        initial = super(SprintUpdate, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])

        initial['sprint'] = sprint

        return initial

    def get_context_data(self, **kwargs):
        context = super(SprintUpdate, self).get_context_data(**kwargs)
        self.sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        context['sprint'] = self.sprint
        return context

    def get_form_kwargs(self):
        """
        Metodo que inserta los formularios con los argumentos clave.
        """
        kwargs = super(SprintUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class SprintBacklogIndexView(generic.ListView):
    """
    Clase que despliega la lista completa de user stories del sprints en el Index
    de la aplicacion sprints_backlog.

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    template_name = 'sprints/sprint_backlog.html'
    context_object_name = 'userstory_list'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        self.sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return UserStory.objects.filter(sprint=self.sprint).exclude(estado='Descartado').order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super(SprintBacklogIndexView, self).get_context_data(**kwargs)
        context['sprint'] = self.sprint
        context['proyecto'] = self.proyecto

        return context


class SprintGestionar(UpdateView):
    """
    Clase que se utiliza para asignar y gestionar los user stories del sprint
    """
    #form_class = SprintAsignarUserStoryForm
    template_name = 'sprints/sprint_gestionar.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @return: objeto de Sprint
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la gestion del user story es exitosa
        @return: redireccion al index de gestion de sprints
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:gestionar', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return: clave
        """
        kwargs = super(SprintGestionar, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return: copia de sprint
        """
        initial = super(SprintGestionar, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])

        solo_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "solo_del_proyecto = %s" % solo_del_proyecto
        users_rol_developer = []
        for rol in solo_del_proyecto:
            if rol.rol_proyecto.group.name == "Developer":
                users_rol_developer.append(rol.user)

        print "rol_developer = %s" % users_rol_developer

        initial['sprint'] = sprint
        initial['proyecto'] = proyecto
        initial['users_rol_developer'] = users_rol_developer

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
        """
        context = super(SprintGestionar, self).get_context_data(**kwargs)
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story_list_proyecto = UserStory.objects.filter(
            proyecto=proyecto).exclude(Q(estado='Activo') |
                                       Q(estado='Descartado') |
                                       Q(estado='Finalizado') |
                                       Q(estado='Aprobado') |
                                       Q(sprint=sprint)).order_by('-prioridad')
        user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
        context['sprint'] = sprint
        context['proyecto'] = proyecto
        context['user_story_list_proyecto'] = user_story_list_proyecto
        context['user_story_list_sprint'] = user_story_list_sprint

        rol_developer = RolProyecto.objects.get(group__name='Developer')
        miembros = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer)
        cantidad_developers = miembros.count()

        horas_asignadas_sprint = 0
        for us in user_story_list_sprint:
            horas_asignadas_sprint = horas_asignadas_sprint + us.estimacion

        horas_totales_sprint = 0
        for miembro in miembros:
            horas_developer_sprint = 0
            horas_developer_sprint = miembro.horas_developer * sprint.duracion
            horas_totales_sprint = horas_totales_sprint + horas_developer_sprint

        #horas_totales_sprint = sprint.duracion * cantidad_developers * 8
        horas_disponibles = horas_totales_sprint - horas_asignadas_sprint
        context['cantidad'] = cantidad_developers
        context['horas_asignadas_sprint'] = horas_asignadas_sprint
        context['horas_disponibles'] = horas_disponibles
        context['horas_totales_sprint'] = horas_totales_sprint

        return context


def sprint_gestionar(request, pk_proyecto, pk_sprint):

    template = 'sprints/sprint_gestionar.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story_list_proyecto = UserStory.objects.filter(
        proyecto=proyecto).exclude(Q(estado='Activo') |
                                   Q(estado='Descartado') |
                                   Q(estado='Finalizado') |
                                   Q(estado='Aprobado') |
                                   Q(sprint=sprint)).order_by('-prioridad')
    user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
    #context['sprint'] = sprint
    #context['proyecto'] = proyecto
    #context['user_story_list_proyecto'] = user_story_list_proyecto
    #context['user_story_list_sprint'] = user_story_list_sprint

    rol_developer = RolProyecto.objects.get(group__name='Developer')
    miembros = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer)
    cantidad_developers = miembros.count()

    horas_asignadas_sprint = 0
    for us in user_story_list_sprint:
        horas_asignadas_sprint = horas_asignadas_sprint + us.estimacion

    horas_totales_sprint = 0
    for miembro in miembros:
        horas_developer_sprint = 0
        horas_developer_sprint = miembro.horas_developer * sprint.duracion
        horas_totales_sprint = horas_totales_sprint + horas_developer_sprint

    #horas_totales_sprint = sprint.duracion * cantidad_developers * 8
    horas_disponibles = horas_totales_sprint - horas_asignadas_sprint

    return render(request, template, locals())


class SprintAsignar(UpdateView):
    """
    Clase que se utiliza para asignar los user stories al sprint
    """
    form_class = SprintAsignarUserStoryForm
    template_name = 'sprints/asignar_sprint.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @return: objeto de Sprint
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la asignacion del user story es exitosa
        @return: redireccion al index de gestion de sprints
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:gestionar', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return: clave
        """
        kwargs = super(SprintAsignar, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return: copia de sprint
        """
        initial = super(SprintAsignar, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        solo_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "solo_del_proyecto = %s" % solo_del_proyecto
        users_rol_developer = []
        for rol in solo_del_proyecto:
            if rol.rol_proyecto.group.name == "Developer":
                users_rol_developer.append(rol.user)

        print "rol_developer = %s" % users_rol_developer

        initial['sprint'] = sprint
        initial['proyecto'] = proyecto
        initial['user_story'] = user_story
        initial['users_rol_developer'] = users_rol_developer

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
        """
        context = super(SprintAsignar, self).get_context_data(**kwargs)
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        context['sprint'] = sprint
        context['proyecto'] = proyecto
        context['user_story'] = user_story


        return context


def detalle_horas(request, pk_proyecto, pk_sprint):
    """
    Funcion que permite ver el detalle de la asignacion de horas en un sprint.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/detalle_horas.html para obtener el detalle de horas.
    """
    template = 'sprints/detalle_horas.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
    usuario = request.user


    rol_developer = RolProyecto.objects.get(group__name='Developer')
    lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
    cantidad_developers = lista_developers.count()


    dic = {}
    for arr in lista_developers:
        dic[arr.pk] = arr

    dev_horas_disponibles = []
    dev_horas_asignadas = []
    dev_total_horas = []
    dev_porcentaje = []
    for developer in lista_developers:
        user_story_list_sprint_usuario = UserStory.objects.filter(usuario=developer.user, sprint=sprint)
        total_horas_us_user = 0
        for us in user_story_list_sprint_usuario:
            total_horas_us_user = total_horas_us_user + us.estimacion
        dev_horas_disponibles.append(developer.horas_developer * sprint.duracion - total_horas_us_user)
        dev_horas_asignadas.append(total_horas_us_user)
        dev_total_horas.append(developer.horas_developer * sprint.duracion)
        dev_porcentaje.append(total_horas_us_user*100/(developer.horas_developer * sprint.duracion))


    horas_asignadas_sprint = 0
    for us in user_story_list_sprint:
        horas_asignadas_sprint = horas_asignadas_sprint + us.estimacion

    horas_totales_sprint = 0
    for miembro in lista_developers:
        horas_developer_sprint = 0
        horas_developer_sprint = miembro.horas_developer * sprint.duracion
        horas_totales_sprint = horas_totales_sprint + horas_developer_sprint

    #horas_totales_sprint = sprint.duracion * cantidad_developers * 8

    horas_disponibles = horas_totales_sprint - horas_asignadas_sprint

    return render(request, template, locals())


class SprintGestionarUpdate(UpdateView):
    """
    Clase que se utiliza para modificar la asignacion de los user stories del sprint
    """
    form_class = SprintUpdateUserStoryForm
    template_name = 'sprints/sprint_gestionar_update.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @param queryset:
        @return: objeto de Sprint
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la gestion del user story es exitosa
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:gestionar', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return:
        """
        kwargs = super(SprintGestionarUpdate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return:
        """
        initial = super(SprintGestionarUpdate, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        solo_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "solo_del_proyecto = %s" % solo_del_proyecto
        users_rol_developer = []
        for rol in solo_del_proyecto:
            if rol.rol_proyecto.group.name == "Developer":
                users_rol_developer.append(rol.user)

        print "rol_developer = %s" % users_rol_developer

        initial['user_story'] = user_story
        initial['sprint'] = sprint
        initial['proyecto'] = proyecto
        initial['users_rol_developer'] = users_rol_developer

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return: copia de sprint
        """
        context = super(SprintGestionarUpdate, self).get_context_data(**kwargs)
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        self.user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        user_story_list_proyecto = UserStory.objects.filter(
            proyecto=proyecto).exclude(Q(estado='Activo') |
                                       Q(estado='Descartado') |
                                       Q(estado='Finalizado') |
                                       Q(estado='Aprobado') |
                                       Q(sprint=sprint)).order_by('-prioridad')
        user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
        context['user_story'] = self.user_story
        context['sprint'] = sprint
        context['proyecto'] = proyecto
        context['user_story_list_proyecto'] = user_story_list_proyecto
        context['user_story_list_sprint'] = user_story_list_sprint

        return context


@login_required(login_url='/login/')
def desasignar_user_story(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que realiza la desasignacion de un user story a un sprint, flujo y developer
    @param request: user story
    @param pk_proyecto: clave primaria de proyecto
    @param pk_sprint: clave primaria de sprint
    @param pk_user_story: clave primaria de user story
    @return: template con texto renderizado
    """
    template = 'sprints/sprint_gestionar_delete.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)
    usuario = request.user
    if request.method == 'POST':

        if str(user_story.estado) == 'Finalizado' or str(user_story.estado) == 'Aprobado':
            mensaje = 'No se puede desasignar del sprint un user story Finalizado o Aprobado'

            return render(request, template, locals())

        else:
            user_story.estado = 'No asignado'
            user_story.sprint = None
            #user_story.flujo = None
            user_story.usuario = None
            user_story.save()

            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="desarrollador",
                                                  valor='Ninguno', usuario=usuario)
            historial_us.save()
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="sprint",
                                                  valor='Ninguno', usuario=usuario)
            historial_us.save()
            historial_us = HistorialUserStory(user_story=user_story, operacion='modificado', campo="flujo",
                                                  valor='Ninguno', usuario=usuario)
            historial_us.save()


            #detalle = UserStoryDetalle.objects.get(user_story=user_story)
            #detalle.delete()

            return HttpResponseRedirect(reverse('sprints:gestionar', args=[pk_proyecto, pk_sprint]))

    return render(request, template, locals())


@login_required(login_url='/login/')
def iniciar_sprint(request, pk_proyecto, pk_sprint):
    """
    Funcion que realiza la inicializacion del sprint
    @param request: sprint
    @param pk_proyecto: clave primaria de proyecto
    @param pk_sprint: clave primaria de sprint
    @return: redirige al index de Sprints
    """
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    sprint.estado = 'Activo'
    sprint.fecha_inicio = datetime.date.today()
    cant_dias_habiles = 0
    for i in range(0, sprint.duracion+1):
        cant_dias_habiles = habiles(sprint.fecha_inicio, (sprint.fecha_inicio + datetime.timedelta(days=sprint.duracion+i)))
        if cant_dias_habiles == sprint.duracion:
            sprint.fecha_fin = sprint.fecha_inicio + datetime.timedelta(days=sprint.duracion+i)
            break

    sprint.save()


    user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')

    # registrar el inicio del kanban en el user story
    for user_story in user_stories:
        detalle = UserStoryDetalle.objects.get(user_story=user_story)

        tarea = Tarea()
        tarea.user_story = user_story
        tarea.descripcion = "Inicio en el kanban"
        tarea.horas_de_trabajo = 0
        tarea.sprint = sprint
        tarea.flujo = user_story.flujo
        tarea.actividad = user_story.userstorydetalle.actividad
        tarea.estado = detalle.estado
        tarea.tipo = 'Cambio de Estado'
        tarea.usuario = user_story.usuario
        tarea.save()

        historial_us = HistorialUserStory(user_story=user_story, operacion='iniciado', usuario=user_story.usuario)
        historial_us.save()

    return HttpResponseRedirect(reverse('sprints:kanban', args=[pk_proyecto, pk_sprint]))


@login_required(login_url='/login/')
def sprint_kanban(request, pk_proyecto, pk_sprint):
    """
    Funcion que genera el o los tableros kanban que corresponden al sprint
    @param request: objeto de Sprint
    @param pk_proyecto: clave primaria de proyecto
    @param pk_sprint: clave primaria de sprint
    @return: template con texto renderizado
    """
    template = 'sprints/sprint_kanban.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    todos_flujos = Flujo.objects.all()
    user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado')

    flujos_distintos = user_stories.values_list('flujo').distinct()

    print flujos_distintos

    flujos_sprint = []
    for flujo in flujos_distintos:
        flujos_sprint.append(Flujo.objects.get(pk=flujo[0]))

    flujos_sprint = sorted(flujos_sprint, key=attrgetter('pk'))

    #flujos_sprint = Flujo.objects.filter(pk__in=flujos_sprint_t).order_by('pk')
    print flujos_sprint

    return render(request, template, locals())


@login_required(login_url='/login/')
def cambiar_estado(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que cambia el estado y/o la actividad de un user story seleccionado en un flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @type pk_user_story: string
    @param pk_user_story: id del user story

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/sprint_kanban.html para obtener el kanban actual
    """
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)

    actividades = user_story.flujo.actividades.all().order_by('pk')
    #estados = actividades[0].estados.all()
    detalle = UserStoryDetalle.objects.get(user_story=user_story)
    us_original_act = user_story.userstorydetalle.actividad
    us_original_est = user_story.userstorydetalle.estado

    us_id = user_story.id
    uri = request.build_absolute_uri()
    print "uri= %s" % uri

    uri_us = urlparse.urljoin(uri, '../../tareas/%s/' % us_id)
    print "uri_us= %s" % uri_us

    for index, act in enumerate(actividades):
        estados = act.estados.all()
        if us_original_act == act:
            if us_original_est == estados[0]:
                detalle.estado = estados[1]

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Cambio de estado: %s -> %s" % (estados[0], estados[1])
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = detalle.estado
                tarea.tipo = 'Cambio de Estado'
                tarea.usuario = request.user
                tarea.save()

                #se envia la notificacion a traves de celery
                cambio_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

            elif us_original_est == estados[1] and actividades.reverse()[0] != act:
                detalle.estado = estados[2]

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Cambio de estado: %s -> %s" % (estados[1], estados[2])
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = detalle.estado
                tarea.tipo = 'Cambio de Estado'
                tarea.usuario = request.user
                tarea.save()

                #se envia la notificacion a traves de celery
                cambio_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

            elif us_original_est == estados[2] and actividades.reverse()[0] != act:
                #detalle.estado = estados[2]
                detalle.actividad = actividades[index+1]

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Cambio de actividad: %s -> %s" % (act, actividades[index+1])
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = detalle.actividad
                est = actividades[index+1].estados.all()
                tarea.estado = est[0]
                tarea.tipo = 'Cambio de Estado'
                tarea.usuario = request.user
                tarea.save()

                detalle.estado = est[0]

                #se envia la notificacion a traves de celery
                cambio_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

            elif us_original_est == estados[1] and actividades.reverse()[0] == act:
                detalle.estado = estados[2]

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Cambio de estado: %s -> %s" % (estados[1], estados[2])
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = detalle.estado
                tarea.tipo = 'Cambio de Estado'
                tarea.usuario = request.user
                tarea.save()

                #se envia la notificacion a traves de celery
                cambio_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

            elif us_original_est == estados[2] and actividades.reverse()[0] == act:

                user_story.estado = 'Finalizado'

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Finalizar user story"
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = detalle.estado
                tarea.tipo = 'Cambio de Estado'
                tarea.usuario = request.user
                tarea.save()

                historial_us = HistorialUserStory(user_story=user_story, operacion='finalizado', usuario=request.user)
                historial_us.save()

                #se envia la notificacion a traves de celery
                fin_user_story.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

    detalle.save()
    user_story.save()

    return HttpResponseRedirect(reverse('sprints:kanban', args=[pk_proyecto, pk_sprint]))


def revertir_estado(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que revierte el estado y/o la actividad de un user story seleccionado en un flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @type pk_user_story: string
    @param pk_user_story: id del user story

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/sprint_kanban.html para obtener el kanban actual
    """
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)

    actividades = user_story.flujo.actividades.all().order_by('pk')
    #estados = actividades[0].estados.all()
    detalle = UserStoryDetalle.objects.get(user_story=user_story)
    us_original_act = user_story.userstorydetalle.actividad
    us_original_est = user_story.userstorydetalle.estado

    us_id = user_story.id
    uri = request.build_absolute_uri()
    print "uri= %s" % uri

    uri_us = urlparse.urljoin(uri, '../../tareas/%s/' % us_id)
    print "uri_us= %s" % uri_us

    for index, act in enumerate(actividades):
        estados = act.estados.all()
        if us_original_act == act:

            if actividades[0] != us_original_act:

                if user_story.estado == 'Activo' and us_original_est != estados[0]:
                    #detalle.actividad = actividades[index-1]

                    tarea = Tarea()
                    tarea.user_story = user_story
                    tarea.descripcion = "Revertir: - Estado: %s -> %s" % (us_original_est, estados[0])
                    tarea.horas_de_trabajo = 0
                    tarea.sprint = sprint
                    tarea.flujo = user_story.flujo
                    tarea.actividad = us_original_act
                    est = actividades[index].estados.all()
                    tarea.estado = est[0]
                    tarea.tipo = 'Cambio de Estado'
                    tarea.usuario = request.user
                    #tarea.estado = detalle.estado
                    tarea.save()
                    detalle.estado = est[0]

                    #se envia la notificacion a traves de celery
                    reversion_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

                if user_story.estado == 'Activo' and us_original_est == estados[0]:
                    detalle.actividad = actividades[index-1]

                    tarea = Tarea()
                    tarea.user_story = user_story
                    tarea.descripcion = "Revertir: - Actividad: %s -> %s" % (us_original_act, actividades[index-1])
                    tarea.horas_de_trabajo = 0
                    tarea.sprint = sprint
                    tarea.flujo = user_story.flujo
                    tarea.actividad = detalle.actividad
                    est = actividades[index-1].estados.all()
                    tarea.estado = est[0]
                    tarea.tipo = 'Cambio de Estado'
                    tarea.usuario = request.user
                    #tarea.estado = detalle.estado
                    tarea.save()
                    detalle.estado = est[0]

                    #se envia la notificacion a traves de celery
                    reversion_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

                if user_story.estado == 'Finalizado':
                    detalle.actividad = actividades[index]

                    tarea = Tarea()
                    tarea.user_story = user_story
                    tarea.descripcion = "Revertir: - Estado: %s -> %s" % (us_original_est, actividades[index].estados.all()[0])
                    tarea.horas_de_trabajo = 0
                    tarea.sprint = sprint
                    tarea.flujo = user_story.flujo
                    tarea.actividad = detalle.actividad
                    est = actividades[index].estados.all()
                    tarea.estado = est[0]
                    tarea.tipo = 'Cambio de Estado'
                    tarea.usuario = request.user
                    #tarea.estado = detalle.estado
                    tarea.save()
                    detalle.estado = est[0]
                    user_story.estado = 'Activo'

                    #se envia la notificacion a traves de celery
                    reversion_estado.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

    detalle.save()
    user_story.save()

    return HttpResponseRedirect(reverse('sprints:kanban', args=[pk_proyecto, pk_sprint]))

@login_required(login_url='/login/')
def aprobar_user_story(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que permite aprobar un user story finalizado en un flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @type pk_user_story: string
    @param pk_user_story: id del user story

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/sprint_kanban.html para obtener el kanban actual
    """

    template = 'sprints/user_story_aprobar.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)
    usuario = request.user
    detalle = UserStoryDetalle.objects.get(user_story=user_story)
    lista_tareas_us = Tarea.objects.filter(user_story=user_story)
    horas_acumuladas = 0

    us_id = user_story.id
    uri = request.build_absolute_uri()
    print "uri= %s" % uri

    uri_us = urlparse.urljoin(uri, '../../tareas/%s/' % us_id)
    print "uri_us= %s" % uri_us

    for tarea in lista_tareas_us:
        horas_acumuladas = horas_acumuladas + tarea.horas_de_trabajo

    if request.method == 'POST':
        form = AgregarNotaForm(request.POST, request.user, initial={'user_story': user_story})

        if form.is_valid:
            user_story.estado = 'Aprobado'
            user_story.save()

            tarea = Tarea()
            tarea.user_story = user_story
            tarea.descripcion = "Aprobar user story"
            tarea.horas_de_trabajo = 0
            tarea.sprint = sprint
            tarea.flujo = user_story.flujo
            tarea.actividad = user_story.userstorydetalle.actividad
            tarea.estado = user_story.userstorydetalle.estado
            tarea.tipo = 'Cambio de Estado'
            tarea.usuario = request.user
            tarea.save()

            historial_us = HistorialUserStory(user_story=user_story, operacion='aprobado', usuario=request.user)
            historial_us.save()

            #se envia la notificacion a traves de celery
            aprobacion_user_story.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

            print "en view nota"

            return HttpResponseRedirect(reverse('sprints:kanban', args=[pk_proyecto, pk_sprint]))

    else:
        form = AgregarNotaForm(request.user, initial={'user_story': user_story})

    return render(request, template, locals())


class AprobarUserStory(UpdateView):
    """
    Clase que permite aprobar el user story
    """
    form_class = AgregarNotaForm
    template_name = 'sprints/user_story_aprobar.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @return: objeto de Sprint
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la aprobacion es exitosa
        @return: redirige al template de kanban
        """
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        us_id = user_story.id
        uri = self.request.build_absolute_uri()

        uri_us = urlparse.urljoin(uri, '../../tareas/%s/' % us_id)

        print "uri_us= %s en success" % uri_us

        #se envia la notificacion a traves de celery
        aprobacion_user_story.delay(proyecto.nombre_corto, sprint.nombre, user_story.nombre, user_story.flujo.nombre, uri_us)

        return reverse('sprints:kanban', args=[proyecto.pk, sprint.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return: formulario de tareas
        """
        kwargs = super(AprobarUserStory, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return: formulario completado
        """
        initial = super(AprobarUserStory, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        solo_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "solo_del_proyecto = %s" % solo_del_proyecto
        users_rol_developer = []
        for rol in solo_del_proyecto:
            if rol.rol_proyecto.group.name == "Developer":
                users_rol_developer.append(rol.user)

        print "rol_developer = %s" % users_rol_developer

        initial['user_story'] = user_story
        initial['sprint'] = sprint
        initial['proyecto'] = proyecto
        initial['users_rol_developer'] = users_rol_developer

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return: diccionario con el contexto del template
        """
        context = super(AprobarUserStory, self).get_context_data(**kwargs)
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        self.user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        user_story_list_proyecto = UserStory.objects.filter(
            proyecto=proyecto).exclude(Q(estado='Activo') |
                                       Q(estado='Descartado') |
                                       Q(estado='Finalizado') |
                                       Q(estado='Aprobado') |
                                       Q(sprint=sprint)).order_by('-prioridad')
        user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')

        detalle = UserStoryDetalle.objects.get(user_story=self.user_story)
        lista_tareas_us = Tarea.objects.filter(user_story=self.user_story)
        horas_acumuladas = 0

        us_id = self.user_story.id
        uri = self.request.build_absolute_uri()
        print "uri= %s" % uri

        uri_us = urlparse.urljoin(uri, '../../tareas/%s/' % us_id)
        print "uri_us= %s" % uri_us

        for tarea in lista_tareas_us:
            horas_acumuladas = horas_acumuladas + tarea.horas_de_trabajo

        #nota = Nota.objects.get(user_story=self.user_story)
        #print "nota.texto = %s" % nota.texto

        context['user_story'] = self.user_story
        context['sprint'] = sprint
        context['proyecto'] = proyecto
        context['user_story_list_proyecto'] = user_story_list_proyecto
        context['user_story_list_sprint'] = user_story_list_sprint
        #context['nota'] = nota.texto

        return context


class RegistrarTarea(UpdateView):
    """
    Clase que permite registrar la tarea realizada sobre el user story
    """
    form_class = RegistrarTareaForm
    template_name = 'sprints/registrar_tarea.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @return: objeto de Sprint
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si el registro de la tarea es exitoso
        @return: redirige al template de kanban
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:kanban', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return: formulario de tareas
        """
        kwargs = super(RegistrarTarea, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return: formulario completado
        """
        initial = super(RegistrarTarea, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])

        solo_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "solo_del_proyecto = %s" % solo_del_proyecto
        users_rol_developer = []
        for rol in solo_del_proyecto:
            if rol.rol_proyecto.group.name == "Developer":
                users_rol_developer.append(rol.user)

        print "rol_developer = %s" % users_rol_developer

        initial['user_story'] = user_story
        initial['sprint'] = sprint
        initial['proyecto'] = proyecto
        initial['users_rol_developer'] = users_rol_developer

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return: diccionario con el contexto del template
        """
        context = super(RegistrarTarea, self).get_context_data(**kwargs)
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        self.user_story = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        user_story_list_proyecto = UserStory.objects.filter(
            proyecto=proyecto).exclude(Q(estado='Activo') |
                                       Q(estado='Descartado') |
                                       Q(estado='Finalizado') |
                                       Q(estado='Aprobado') |
                                       Q(sprint=sprint)).order_by('-prioridad')
        user_story_list_sprint = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')
        context['user_story'] = self.user_story
        context['sprint'] = sprint
        context['proyecto'] = proyecto
        context['user_story_list_proyecto'] = user_story_list_proyecto
        context['user_story_list_sprint'] = user_story_list_sprint

        return context


class TareasIndexView(generic.ListView):
    """
    Clase que despliega la lista de tareas realizadas en un user story
    """
    template_name = 'sprints/ver_tareas.html'

    def get_queryset(self):
        """
        Metodo que realiza el filtrado de la lista de tareas a mostrar en la vista
        @return: tarea especifica
        """
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])

        return Tarea.objects.filter(user_story=self.user_story).order_by('-fecha')

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return: template completado
        """
        context = super(TareasIndexView, self).get_context_data(**kwargs)
        sprint = get_object_or_404(Sprint, pk=self.kwargs['pk_sprint'])
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])

        lista_tareas_us = Tarea.objects.filter(user_story=self.user_story)
        horas_acumuladas = 0

        for tarea in lista_tareas_us:
            horas_acumuladas = horas_acumuladas + tarea.horas_de_trabajo

        lista_archivos = Adjunto.objects.filter(user_story=self.user_story)
        cantidad_archivos = lista_archivos.count()

        self.user_story.horas_acumuladas = horas_acumuladas

        tipos_tareas = ['Registro de Tarea', 'Cambio de Estado']

        try:
            nota = Nota.objects.get(user_story=self.user_story)
            print "nota = %s" % nota
        except ObjectDoesNotExist:
            nota = ""

        context['proyecto'] = proyecto
        context['sprint'] = sprint
        context['user_story'] = self.user_story
        context['horas_acumuladas'] = self.user_story.horas_acumuladas
        context['cantidad_archivos'] = cantidad_archivos
        context['tipos_tareas'] = tipos_tareas
        context['nota'] = nota

        return context


def adjuntar_archivo(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que permite adjuntar un archivo a un user story seleccionado en un flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @type pk_user_story: string
    @param pk_user_story: id del user story

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/sprint_kanban.html para obtener el kanban actual
    """

    template = 'sprints/user_story_adjuntar_archivo.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)
    usuario = request.user
    detalle = UserStoryDetalle.objects.get(user_story=user_story)

    lista_archivos = Archivo.objects.filter(user_story=user_story)

    # nota = Nota.objects.get(user_story=user_story)

    if request.method == 'POST':
        form = AdjuntarArchivoForm(request.POST, request.FILES)

        try:
            if form.is_valid:
                nuevo_archivo = Archivo(user_story=user_story, archivo=request.FILES['archivo'])
                #nuevo_archivo.user_Story = user_story
                nuevo_archivo.save()

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Adjuntar archivo"
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = user_story.userstorydetalle.estado
                tarea.tipo = 'Registro de Tarea'
                tarea.usuario = request.user
                tarea.save()

                return HttpResponseRedirect(reverse('sprints:adjuntar_archivo', args=[pk_proyecto, pk_sprint, pk_user_story]))
        except Exception, e:
            print e
            mensaje = 'No se pudo subir el archivo.'
            return render(request, 'sprints/user_story_adjuntar_archivo.html', locals())

    else:
        form = AdjuntarArchivoForm()

    return render(request, template, locals())


def agregar_adjunto(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Funcion que permite adjuntar un archivo a un user story seleccionado en un flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_proyecto: string
    @param pk_proyecto: id del proyecto

    @type pk_sprint: string
    @param pk_sprint: id del sprint

    @type pk_user_story: string
    @param pk_user_story: id del user story

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza sprints/sprint_kanban.html para obtener el kanban actual
    """

    template = 'sprints/user_story_agregar_adjunto.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)
    usuario = request.user
    detalle = UserStoryDetalle.objects.get(user_story=user_story)

    lista_archivos = Adjunto.objects.filter(user_story=user_story)

    # nota = Nota.objects.get(user_story=user_story)

    if request.method == 'POST':
        form = AgregarAdjuntoForm(request.POST)

        try:
            if form.is_valid:
                nuevo_archivo = Adjunto(user_story=user_story, archivo=request.FILES['archivo'])
                #nuevo_archivo.user_Story = user_story
                nuevo_archivo.save()
                #form.save()

                tarea = Tarea()
                tarea.user_story = user_story
                tarea.descripcion = "Adjuntar archivo"
                tarea.horas_de_trabajo = 0
                tarea.sprint = sprint
                tarea.flujo = user_story.flujo
                tarea.actividad = user_story.userstorydetalle.actividad
                tarea.estado = user_story.userstorydetalle.estado
                tarea.tipo = 'Registro de Tarea'
                tarea.usuario = request.user
                tarea.save()

                exito = "Archivo agregado"

                return render(request, template, locals())

                #return HttpResponseRedirect(reverse('sprints:agregar_adjunto', args=[pk_proyecto, pk_sprint, pk_user_story]))
            else:
                mensaje = 'Seleccione un archivo.'
                return render(request, 'sprints/user_story_agregar_adjunto.html', locals())
        except Exception, e:
            print e
            mensaje = 'No se pudo subir el archivo.'
            return render(request, 'sprints/user_story_agregar_adjunto.html', locals())

    else:
        form = AgregarAdjuntoForm()

    return render(request, template, locals())


class TareasIndexViewAjax(generic.TemplateView):
    """
    Clase que despliega la lista de tareas realizadas en un user story utilizando Ajax para el filtrado
    """

    def get(self, request, *args, **kwargs):
        """
        Metodo que obtiene los datos a ser enviados al template de la vista

        @type self: FormView
        @param self: Informacion sobre la vista actual

        @type request: django.http.HttpRequest
        @param request: Contiene informacion sobre la peticion actual

        @rtype: django.http.HttpResponse
        @return: Renderiza sprints/ver_tareas.html para obtener las tareas del user story
        """
        tipo_tarea = request.GET['tipo']
        print "tipo_tarea= %s" % tipo_tarea

        user_story_id = request.GET['id_us']
        print "us= %s" % user_story_id

        tareas_x_tipo = Tarea.objects.filter(user_story__id=user_story_id, tipo=tipo_tarea).order_by('-fecha')
        print tareas_x_tipo

        locale.setlocale(locale.LC_ALL, 'es_PY.utf8')

        if tareas_x_tipo:
            lista = []
            for tarea in tareas_x_tipo:
                #fecha = str(tarea.fecha)
                lista.append({'descripcion': tarea.descripcion, 'horas_de_trabajo': tarea.horas_de_trabajo,
                              'sprint': tarea.sprint.nombre, 'flujo': tarea.flujo.nombre,
                              'actividad': tarea.actividad.nombre, 'estado': tarea.estado.nombre,
                              'usuario': tarea.usuario.username,
                              'fecha': tarea.fecha.strftime('%d/%m/%Y')})
            print tarea.fecha
            #print fecha
            data = json.dumps(lista)

            #data = serializers.serialize('json', tareas_x_tipo,
            #                             fields=('descripcion', 'horas_de_trabajo', 'actividad_tarea', 'estado', 'fecha'))

            print data

        elif tipo_tarea == 'Todas las tareas' and Tarea.objects.filter(user_story__id=user_story_id):
            todas = Tarea.objects.filter(user_story__id=user_story_id).order_by('-fecha')
            print todas

            lista = []
            for tarea in todas:
                #fecha = str(tarea.fecha)
                lista.append({'descripcion': tarea.descripcion, 'horas_de_trabajo': tarea.horas_de_trabajo,
                              'sprint': tarea.sprint.nombre, 'flujo': tarea.flujo.nombre,
                              'actividad': tarea.actividad.nombre, 'estado': tarea.estado.nombre,
                              'usuario': tarea.usuario.username,
                              'fecha': tarea.fecha.strftime('%d/%m/%Y')})
            print tarea.fecha
            #print fecha
            data = json.dumps(lista)

        else:
            print "sin tipo"
            data = [{}]
            return HttpResponse(data, content_type='application/json')

        return HttpResponse(data, content_type='application/json')


@login_required(login_url='/login/')
def burndown_chart(request, pk_proyecto, pk_sprint):
    """
    Funcion que genera el burndown chart que corresponde al sprint
    @param request: objeto de Sprint
    @param pk_proyecto: clave primaria de proyecto
    @param pk_sprint: clave primaria de sprint
    @return: template con texto renderizado
    """
    template = 'sprints/burndown_chart.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    #todos_flujos = Flujo.objects.all()
    user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado')

    duracion = sprint.duracion

    lista_tareas_us_sprint = Tarea.objects.filter(sprint=sprint, tipo='Registro de Tarea')
    horas_totales_acumuladas = 0
    for tarea in lista_tareas_us_sprint:
        horas_totales_acumuladas = horas_totales_acumuladas + tarea.horas_de_trabajo

    horas_calculadas_chart = 0

    user_stories_lista = []

    lista_data = []
    horas_totales_estimacion = 0
    for us in user_stories:
        #fecha = str(us.fecha)

        horas_totales_estimacion = horas_totales_estimacion + us.estimacion

        user_stories_lista.append({'year': us.nombre, 'value': us.estimacion})

    user_stories_json = json.dumps(user_stories_lista)
    print "horas_tot_ estimacion %s" % horas_totales_estimacion
    calculado = horas_totales_estimacion
    calculado2 = horas_totales_estimacion


    rol_developer = RolProyecto.objects.get(group__name='Developer')
    lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
    cantidad_developers = lista_developers.count()

    horas_totales_sprint = 0
    horas_developers_sprint_dia = 0
    for miembro in lista_developers:
        horas_developers_sprint_dia = horas_developers_sprint_dia + miembro.horas_developer
        #horas_totales_sprint = horas_totales_sprint + horas_developer_sprint


    #while tarea.fecha.date() <= sprint.fecha_fin:
    #    pass
    #for dia in range(1, duracion+1):
    day = 0
    dia = 1
    lista_data.append({'year': 0, 'value2': calculado2, 'value': calculado})
    print "antes while"
    while sprint.fecha_inicio+datetime.timedelta(days=day) <= sprint.fecha_fin:
        print "fecha days = %s" % str(sprint.fecha_inicio+datetime.timedelta(days=day))
        print "fecha_fin = %s" % sprint.fecha_fin

        print "Dia %s" % dia
        print "calculado = %s" % calculado
        print "calculado2 = %s" % calculado2
        #calculado = horas_totales_estimacion
        #entro = False
        for tarea in lista_tareas_us_sprint:

            print "tareafecha %s, sprint_inicio %s" % (tarea.fecha, sprint.fecha_inicio)
            if tarea.fecha.date() == sprint.fecha_inicio+datetime.timedelta(days=day):
                #entro = True
                print "if"
                print "estado %s" % tarea.user_story.estado
                if calculado >= 0:
                    calculado = calculado - tarea.horas_de_trabajo

                    print "calculado = %s" % calculado

        #if entro:
        dia_semana = (sprint.fecha_inicio+datetime.timedelta(days=day)).weekday()
        print "dia_semana %s" % dia_semana
        if dia_semana < 5:
            calculado2 = calculado2 - horas_developers_sprint_dia
            print "calculado2 = %s" % calculado2
            lista_data.append({'year': dia, 'value2': calculado2, 'value': calculado})
            dia = dia + 1

        day = day + 1



    calculado_json = json.dumps(lista_data)
    #print "calculado_json" % str(calculado_json)
    print lista_data

    return render(request, template, locals())


@login_required(login_url='/login/')
def finalizar_sprint(request, pk_proyecto, pk_sprint):
    """
    Funcion que realiza la finalizacion del sprint
    @param request: sprint
    @param pk_proyecto: clave primaria de proyecto
    @param pk_sprint: clave primaria de sprint
    @return: redirige al index de Sprints
    """
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    template = 'sprints/finalizar_sprint.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    user_stories = UserStory.objects.filter(sprint=sprint, estado='Activo')

    if request.method == 'POST':

        sprint.estado = 'Finalizado'
        print "fecha = %s" % datetime.date.today()
        sprint.fecha_fin = datetime.date.today()

        sprint.save()

        for us in user_stories:
            us.estado = 'Pendiente'
            us.save()

        return HttpResponseRedirect(reverse('sprints:index', args=[pk_proyecto]))
    if user_stories:
        mensaje = 'Existen user stories que no han finalizado.'

    return render(request, template, locals())


@login_required(login_url='/login/')
def descartar_user_story(request, pk_proyecto, pk_sprint, pk_user_story):
    """
    Metodo que descarta un user story

    @param request:
    @type

    @param pk_proyecto: clave primaria del proyecto al cual corresponde el user story
    @type

    @param pk_user_story: clave primaria del user story
    @type

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza user_stories/delete.html para obtener el formulario o
            redirecciona a la vista index del sprint backlog de User Stories si el user story fue descartado.
    """
    template = 'sprints/user_story_descartar.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)
    user_story = get_object_or_404(UserStory, pk=pk_user_story)
    usuario = request.user
    if request.method == 'POST':

        if str(user_story.estado) == 'Finalizado' or str(user_story.estado) == 'Aprobado':
            mensaje = 'No se puede descartar un user story Finalizado o Aprobado'

            return render(request, template, locals())

        else:
            user_story.estado = 'Descartado'
            user_story.save()

            historial_us = HistorialUserStory(user_story=user_story, operacion='descartado', usuario=usuario)
            historial_us.save()

            return HttpResponseRedirect(reverse('sprints:backlog', args=[proyecto.pk, sprint.pk]))

    return render(request, template, locals())