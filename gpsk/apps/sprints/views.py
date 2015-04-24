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
    form_class = SprintCreateForm
    template_name = 'sprints/create.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('sprints:index', args=[obj.pk])

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(SprintCreate, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs

    #@method_decorator(permission_required('sprints.crear_sprint'))
    #def dispatch(self, *args, **kwargs):
    #    return super(SprintCreate, self).dispatch(*args, **kwargs)


class SprintUpdate(UpdateView):
    form_class = SprintUpdateForm
    template_name = 'sprints/update.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('sprints:index', args=[obj.pk])

    def get_initial(self):
        initial = super(SprintUpdate, self).get_initial()
        sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        flujos_sprint = sprint.flujos
        #flujos_row = Sprint.objects.values('flujos').distinct()
        #flujos = Flujo.objects.filter(pk__in=sprint.flujos)

        flujos = []
        for f in flujos_sprint.all():
            flujos.append(f)

        initial['sprint'] = sprint
        initial['flujos'] = flujos

        # hs = roles_proyecto_del_usuario.name
        # print hs
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SprintUpdate, self).get_context_data(**kwargs)
        # Add in the publisher
        self.sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        context['sprint'] = self.sprint
    #    self.user = self.request.user
    #    context['user'] = self.user
        #print "Roles %s" % self.roles_de_proyecto
        #context['roles_de_proyecto'] = self.r_proyecto
        #print "Roles %s" % self.r_proyecto
        return context

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(SprintUpdate, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs


class SprintBacklogIndexView(generic.ListView):
    template_name = 'sprints/sprint_backlog.html'
    context_object_name = 'userstory_list'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        self.sprint = Sprint.objects.get(pk=self.kwargs['pk_sprint'])
        return UserStory.objects.filter(sprint=self.sprint).exclude(estado='Descartado').order_by('nombre')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SprintBacklogIndexView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['sprint'] = self.sprint
        context['proyecto'] = self.proyecto

        return context