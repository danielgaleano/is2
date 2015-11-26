from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission

from models import UserStory, HistorialUserStory
from forms import UserStoryCreateForm, UserStoryUpdateFormPO, UserStoryUpdateFormSM, UserStoryCreateFormSM
from apps.proyectos.models import Proyecto
from apps.roles_proyecto.models import RolProyecto_Proyecto


class IndexView(generic.ListView):
    """
    Clase que despliega la lista de user stories del proyecto para su modificacion

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    #model = UserStory
    template_name = 'user_stories/index.html'

    def get_queryset(self):
        """
        Metodo que filtra los user story correspondientes al proyecto

        @rtype: django.db.models.query.Querysets
        @return: resultado de la consulta
        """
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        queryset = RolProyecto_Proyecto.objects.filter(proyecto=self.kwargs['pk_proyecto'])
        self.roles_de_proyecto = get_list_or_404(queryset, user=self.request.user)

        #print "roles de proyecto %s" % self.roles_de_proyecto

        permisos = self.roles_de_proyecto[0].rol_proyecto.group.permissions
        todos_permisos = []
        self.todos_permisos = permisos.all()
        #print "permisos del rol de proyecto"
        #print "permisos todos %s" % todos_permisos
        #print permisos.all()
        for permiso in permisos.all():
            pass
            #print "- %s" % permiso

        el_permiso = Permission.objects.get(codename='crear_userstory')
        #print "El permiso %s" % el_permiso
        tiene = False

        if el_permiso in permisos.all():
            tiene = True

        #print tiene

        return UserStory.objects.filter(proyecto=self.proyecto).order_by('nombre')

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna un diccionario que representa el contexto del template.

        @type
        @param kwargs: la clave primaria del proyecto

        @rtype: context
        @return: El diccionario
        """

        context = super(IndexView, self).get_context_data(**kwargs)

        context['proyecto'] = self.proyecto
        context['roles_de_proyecto'] = self.roles_de_proyecto
        context['permisos'] = self.todos_permisos

        return context


class UserStoryCreate(UpdateView):
    """
    Clase que despliega el formulario para la creacion de User Stories.

    @ivar form_class: Formulario que se utiliza para la creacion de User Stories
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string

    @ivar context_object_name: Variable de contexto
    @type context_object_name: string
    """
    form_class = UserStoryCreateForm
    template_name = 'user_stories/create.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de User Stories una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_form_kwargs(self):

        kwargs = super(UserStoryCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    #@method_decorator(permission_required('user_stories.crear_userstory'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserStoryCreate, self).dispatch(*args, **kwargs)


class UserStoryCreateSM(UpdateView):
    """
    Clase que despliega el formulario para la creacion de User Stories.

    @ivar form_class: Formulario que se utiliza para la creacion de User Stories
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string

    @ivar context_object_name: Variable de contexto
    @type context_object_name: string
    """
    form_class = UserStoryCreateFormSM
    template_name = 'user_stories/create_sm.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto_sm'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de User Stories una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto_sm'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_form_kwargs(self):

        kwargs = super(UserStoryCreateSM, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    #@method_decorator(permission_required('user_stories.crear_userstory'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserStoryCreateSM, self).dispatch(*args, **kwargs)


class UserStoryUpdatePO(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de User Stories, con privilegio de Product Owner.

    @ivar form_class: Formulario que se utiliza para la modficacion de User Stories
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = UserStoryUpdateFormPO
    template_name = 'user_stories/update.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que obtiene los datos del usuario a ser modificado.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @type queryset: django.db.models.query
        @param queryset: Consulta a la base de datos

        @rtype: User
        @return: Usuario actual a ser modificado
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de User Stories una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers, primary key del proyecto
        @return: redireccion al index de la aplicacion user storie, respecto al proyecto al que corresponde
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_initial(self):
        initial = super(UserStoryUpdatePO, self).get_initial()
        userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        initial['user_story'] = userStory
        print "userStory = %s" % userStory

        return initial

    def get_context_data(self, **kwargs):
        context = super(UserStoryUpdatePO, self).get_context_data(**kwargs)
        self.user_story = userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story'])
        context['user_story'] = self.user_story
        return context

    def get_form_kwargs(self):
        """
        Metodo que inyecta los formularios con sus argumentos principales.
        """
        kwargs = super(UserStoryUpdatePO, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class UserStoryUpdateSM(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de User Stories, con privilegio de Scrum Master.

    @ivar form_class: Formulario que se utiliza para la modficacion de User Stories
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = UserStoryUpdateFormSM
    template_name = 'user_stories/update_sm.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        """
        Metodo que obtiene los datos del usuario a ser modificado.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @type queryset: django.db.models.query
        @param queryset: Consulta a la base de datos

        @rtype: Proyecto
        @return: Proyecto actual a ser modificado
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de User Stories una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers, primary key del proyecto
        @return: redireccion al index de la aplicacion user storie, respecto al proyecto al que corresponde
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('user_stories:index', args=[obj.pk])

    def get_initial(self):
        initial = super(UserStoryUpdateSM, self).get_initial()
        userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story_sm'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        initial['user_story'] = userStory
        print "userStorySM = %s" % userStory
        return initial

    def get_context_data(self, **kwargs):
        context = super(UserStoryUpdateSM, self).get_context_data(**kwargs)
        self.user_story = userStory = UserStory.objects.get(pk=self.kwargs['pk_user_story_sm'])
        context['user_story'] = self.user_story
        print "view = %s" % self.user_story.prioridad
        return context

    def get_form_kwargs(self):
        """
        Este metodo inyecta los formularios con sus argumentos principales.
        """
        kwargs = super(UserStoryUpdateSM, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@login_required(login_url='/login/')
def descartar_user_story(request, pk_proyecto, pk_user_story):
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
            redirecciona a la vista index de User Stories si el user story fue descartado.
    """
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

    template_name = 'user_stories/historial.html'
    context_object_name = 'historial_list'

    def get_queryset(self):
        query = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        return HistorialUserStory.objects.filter(user_story=query).order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super(VerHistorialUserStory, self).get_context_data(**kwargs)
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        context['proyecto'] = self.proyecto
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        context['user_story'] = self.user_story
        return context


class VerUserStory(generic.ListView):

    template_name = 'user_stories/ver.html'

    def get_queryset(self):
        user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        return user_story

    def get_context_data(self, **kwargs):
        context = super(VerUserStory, self).get_context_data(**kwargs)
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        context['proyecto'] = self.proyecto
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        context['user_story'] = self.user_story
        return context