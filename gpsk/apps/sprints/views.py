from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from models import Sprint
from forms import SprintCreateForm, SprintUpdateForm
from apps.proyectos.models import Proyecto
from apps.flujos.models import Flujo
from apps.user_stories.models import UserStory
from apps.roles_proyecto.models import RolProyecto_Proyecto
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


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
        flujos_sprint = sprint.flujos

        flujos = []
        for f in flujos_sprint.all():
            flujos.append(f)

        initial['sprint'] = sprint
        initial['flujos'] = flujos

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