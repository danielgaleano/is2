from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from models import UserStory, HistorialUserStory
from forms import UserStoryCreateForm, UserStoryUpdateFormPO, UserStoryUpdateFormSM
from apps.proyectos.models import Proyecto
from apps.roles_proyecto.models import RolProyecto_Proyecto
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class IndexView(generic.ListView):
    #model = UserStory
    template_name = 'user_stories/index.html'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        queryset = RolProyecto_Proyecto.objects.filter(proyecto=self.kwargs['pk_proyecto'])
        self.roles_de_proyecto = get_list_or_404(queryset, user=self.request.user)
        #self.r_proyecto = ""
        #for rol in self.roles_de_proyecto:
        #    print "D"
        #    if rol.rol_proyecto.group.name == u"Product Owner":
        #        self.r_proyecto = rol.rol_proyecto.group.name
        #        print "Inside"
        return UserStory.objects.filter(proyecto=self.proyecto).order_by('nombre')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['proyecto'] = self.proyecto
        context['roles_de_proyecto'] = self.roles_de_proyecto
        #print "Roles %s" % self.roles_de_proyecto
        #context['roles_de_proyecto'] = self.r_proyecto
        #print "Roles %s" % self.r_proyecto
        return context


class UserStoryCreate(UpdateView):
    form_class = UserStoryCreateForm
    template_name = 'user_stories/create.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(UserStoryCreate, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs

    @method_decorator(permission_required('user_stories.crear_userstory'))
    def dispatch(self, *args, **kwargs):
        return super(UserStoryCreate, self).dispatch(*args, **kwargs)

    #def form_valid(self, form):
    #    instance = form.save(commit=True)
    #    instance.user = self.request.user
    #    super(UserStoryCreate, self).save(form)

    #def get_context_data(self, **kwargs):
    #    # Call the base implementation first to get a context
    #    context = super(UserStoryCreate, self).get_context_data(**kwargs)
    #    # Add in the publisher
    #    self.user = self.request.user
    #    context['user'] = self.user
    #   #print "Roles %s" % self.roles_de_proyecto
    #    #context['roles_de_proyecto'] = self.r_proyecto
    #    #print "Roles %s" % self.r_proyecto
    #    return context


class UserStoryUpdatePO(UpdateView):
    form_class = UserStoryUpdateFormPO
    template_name = 'user_stories/update.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_initial(self):
        initial = super(UserStoryUpdatePO, self).get_initial()
        userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        #las filas con la tupla user_rol_proyecto
        #solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        #print "solo_del_usuario = %s" % solo_del_usuario
        #listar los roles en ese proyecto
        #roles_proyecto_del_usuario = solo_del_usuario.values('rol_proyecto').distinct()
        #print "roles_proyecto_del_usuario = %s" % roles_proyecto_del_usuario
        #ropro = Group.objects.filter(rolproyecto__pk__in=roles_proyecto_del_usuario)

        #print "ropro = %s" % ropro

        # dic = {}
        # for i in roles_proyecto_del_usuario:
        #   dic.add(i)
        #pasamos los roles del usuario en el proyecto
        #initial['rolproyecto'] = ropro

        #pasamos el usuario
        initial['user_story'] = userStory
        print "userStory = %s" % userStory

        # hs = roles_proyecto_del_usuario.name
        # print hs
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserStoryUpdatePO, self).get_context_data(**kwargs)
        # Add in the publisher
        self.user_story = userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        context['user_story'] = self.user_story
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
        kwargs = super(UserStoryUpdatePO, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs


class UserStoryUpdateSM(UpdateView):
    form_class = UserStoryUpdateFormSM
    template_name = 'user_stories/update_sm.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_initial(self):
        initial = super(UserStoryUpdateSM, self).get_initial()
        userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story_sm'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        #las filas con la tupla user_rol_proyecto
        #solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        #print "solo_del_usuario = %s" % solo_del_usuario
        #listar los roles en ese proyecto
        #roles_proyecto_del_usuario = solo_del_usuario.values('rol_proyecto').distinct()
        #print "roles_proyecto_del_usuario = %s" % roles_proyecto_del_usuario
        #ropro = Group.objects.filter(rolproyecto__pk__in=roles_proyecto_del_usuario)

        #print "ropro = %s" % ropro

        # dic = {}
        # for i in roles_proyecto_del_usuario:
        #   dic.add(i)
        #pasamos los roles del usuario en el proyecto
        #initial['rolproyecto'] = ropro

        #pasamos el usuario
        initial['user_story'] = userStory
        print "userStorySM = %s" % userStory

        # hs = roles_proyecto_del_usuario.name
        # print hs
        return initial

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(UserStoryUpdateSM, self).get_context_data(**kwargs)
        # Add in the publisher
        self.user_story = userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story_sm'])
        context['user_story'] = self.user_story
        #print "Roles %s" % self.roles_de_proyecto
        #context['roles_de_proyecto'] = self.r_proyecto
        #print "Roles %s" % self.r_proyecto
        return context

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(UserStoryUpdateSM, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs

@login_required(login_url='/login/')
def descartar_user_story(request, pk_proyecto, pk_user_story):
    template = 'user_stories/delete.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
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

            return HttpResponseRedirect(reverse('user_stories:index', args=[proyecto.pk]))

    return render(request, template, locals())


class VerHistorialUserStory(generic.ListView):
    #queryset = HistorialUserStory.objects.filter(user_story=kwargs['pk_user_story']).order_by('-fecha')
    #pk_url_kwarg = 'pk_user_story'
    template_name = 'user_stories/historial.html'
    context_object_name = 'historial_list'

    def get_queryset(self):
        query = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        return HistorialUserStory.objects.filter(user_story=query).order_by('-fecha')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(VerHistorialUserStory, self).get_context_data(**kwargs)
        # Add in the publisher
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        context['proyecto'] = self.proyecto
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        context['user_story'] = self.user_story
        #context['roles_de_proyecto'] = self.roles_de_proyecto
        #print "Roles %s" % self.roles_de_proyecto
        #context['roles_de_proyecto'] = self.r_proyecto
        #print "Roles %s" % self.r_proyecto
        return context