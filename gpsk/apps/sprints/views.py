from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from models import Sprint
from forms import SprintCreateForm, SprintUpdateForm, SprintAsignarUserStoryForm, SprintUpdateUserStoryForm, RegistrarTareaForm
from apps.proyectos.models import Proyecto
from apps.user_stories.models import UserStory, HistorialUserStory, UserStoryDetalle, Tarea
from apps.roles_proyecto.models import RolProyecto_Proyecto
from apps.flujos.models import Flujo


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
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in the publisher
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
        #flujos_sprint = sprint.flujos

        #flujos = []
        #for f in flujos_sprint.all():
        #    flujos.append(f)

        initial['sprint'] = sprint
        #initial['flujos'] = flujos

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
    form_class = SprintAsignarUserStoryForm
    template_name = 'sprints/sprint_gestionar.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que retona el sprint actual
        @param queryset:
        @return:
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la gestion del user story es exitosa
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Proyecto.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:gestionar', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return:
        """
        kwargs = super(SprintGestionar, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return:
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
        #initial['flujos'] = flujos

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

        return context


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
        @return:
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la gestion del user story es exitosa
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Proyecto.objects.get(pk=self.kwargs['pk_sprint'])
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
        #initial['flujos'] = flujos

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
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
    @param request:
    @param pk_proyecto:
    @param pk_sprint:
    @param pk_user_story:
    @return:
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
            user_story.flujo = None
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

            detalle = UserStoryDetalle.objects.get(user_story=user_story)
            detalle.delete()

            return HttpResponseRedirect(reverse('sprints:gestionar', args=[pk_proyecto, pk_sprint]))

    return render(request, template, locals())


@login_required(login_url='/login/')
def iniciar_sprint(request, pk_proyecto, pk_sprint):
    """
    Funcion que realiza la inicializacion del sprint
    @param request:
    @param pk_proyecto:
    @param pk_sprint:
    @return:
    """
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    sprint.estado = 'Activo'
    sprint.save()

    user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado').order_by('nombre')

    #for us in user_stories:
    #    actividades = us.flujo.actividades.all()
    #    estados = actividades[0].estados.all()
    #    detalle = UserStoryDetalle(user_story=us, actividad=actividades[0], estado=estados[0])
    #    detalle.save()

    return HttpResponseRedirect(reverse('sprints:index', args=[pk_proyecto]))


def sprint_kanban(request, pk_proyecto, pk_sprint):
    """
    Funcion que genera el o los tableros kanban que corresponden al sprint
    @param request:
    @param pk_proyecto:
    @param pk_sprint:
    @return:
    """
    template = 'sprints/sprint_kanban.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    sprint = get_object_or_404(Sprint, pk=pk_sprint)

    todos_flujos = Flujo.objects.all()
    user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado')

    #user_story = get_object_or_404(UserStory, pk=pk_user_story)

    flujos_distintos = user_stories.values_list('flujo').distinct()

    print flujos_distintos

    flujos_sprint = []
    for flujo in flujos_distintos:
        flujos_sprint.append(Flujo.objects.get(pk=flujo[0]))

    print flujos_sprint

    return render(request, template, locals())


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
        @param queryset:
        @return:
        """
        obj = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si el registro de la tarea es exitoso
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        obj2 = Proyecto.objects.get(pk=self.kwargs['pk_sprint'])
        return reverse('sprints:kanban', args=[obj.pk, obj2.pk])

    def get_form_kwargs(self):
        """
        Metodo que obtiene el usuario actual del contexto de la vista
        @return:
        """
        kwargs = super(RegistrarTarea, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return:
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
        #initial['flujos'] = flujos

        return initial

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
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
        @return:
        """
        #self.sprint = get_object_or_404(Sprint, pk=self.kwargs['pk_sprint'])
        #self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])

        return Tarea.objects.filter(user_story=self.user_story).order_by('-fecha')

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
        """
        # Call the base implementation first to get a context
        context = super(TareasIndexView, self).get_context_data(**kwargs)
        # Add in the publisher
        sprint = get_object_or_404(Sprint, pk=self.kwargs['pk_sprint'])
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])

        context['proyecto'] = proyecto
        context['sprint'] = sprint
        context['user_story'] = self.user_story

        return context
