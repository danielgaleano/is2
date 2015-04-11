from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from apps.roles_proyecto.models import RolProyecto_Proyecto, RolProyecto
from forms import UserCreateForm, UserUpdateForm, UserAsignarRolesForm, MyPasswordChangeForm
from django.views.generic.edit import FormView

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from django.contrib.auth import update_session_auth_hash


class UserIndexView(generic.ListView):
    """
    Clase que despliega la lista completa de usuarios en el Index
    de la aplicacion Usuarios.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    queryset = User.objects.order_by('username')
    template_name = 'usuarios/index.html'

    #@method_decorator(permission_required('usuarios.listar_usuario'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserIndexView, self).dispatch(*args, **kwargs)


class UserCreate(FormView):
    """
    Clase que despliega el formulario para la creacion de usuarios.

    @ivar form_class: Formulario que se utiliza para la creacion de usuarios
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    template_name = 'usuarios/create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """
        Metodo que guarda el formulario una vez validado.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @type form: django.forms
        @param form: Informacion sobre el formulario actual

        @rtype: FormView
        @return: Constructor que guarda los datos del formulario en la base de datos
        """
        form.save()
        return super(UserCreate, self).form_valid(form)

    def get_success_url(self):
        """
        Metodo que redirecciona al index de usuarios una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        return reverse('usuarios:index')

    #@method_decorator(permission_required('usuarios.crear_usuario'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserCreate, self).dispatch(*args, **kwargs)


class UserUpdate(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de usuarios.

    @ivar form_class: Formulario que se utiliza para la modficacion de usuarios
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    template_name = 'usuarios/update.html'
    form_class = UserUpdateForm
    context_object_name = 'user_detail'

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
        user_actual = User.objects.get(pk=self.kwargs['pk'])
        return user_actual

    def get_success_url(self):
        """
        Metodo que redirecciona al index de usuarios una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        return reverse('usuarios:index')

    #@method_decorator(permission_required('usuarios.modificar_usuario'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserUpdate, self).dispatch(*args, **kwargs)


@login_required(login_url='/login/')
#@permission_required('usuarios.inactivar_usuario')
def inactivar_usuario(request, pk_usuario):
    """
    Funcion que inactiva la cuenta de un usuario seleccionado.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_usuario: string
    @param pk_usuario: id del usuario a ser inactivado

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza usuarios/delete.html para obtener el formulario o
            redirecciona a la vista index de usuarios si el usuario fue desactivado.
    """
    if request.method == 'POST':
        user_detail = get_object_or_404(User, pk=pk_usuario)
        user_detail.is_active = False
        user_detail.save()

        return HttpResponseRedirect('/usuarios/')

    user_detail = get_object_or_404(User, pk=pk_usuario)

    return render(request, 'usuarios/delete.html', locals())


@login_required(login_url='/login/')
#@permission_required('usuarios.activar_usuario')
def activar_usuario(request, pk_usuario):
    """
    Funcion que activa la cuenta de un usuario seleccionado.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_usuario: string
    @param pk_usuario: id del usuario a ser activado

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza usuarios/activate.html para obtener el formulario o
            redirecciona a la vista index de usuarios si el usuario fue activado.
    """
    if request.method == 'POST':
        user_detail = get_object_or_404(User, pk=pk_usuario)
        user_detail.is_active = True
        user_detail.save()

        return HttpResponseRedirect('/usuarios/')

    user_detail = get_object_or_404(User, pk=pk_usuario)

    return render(request, 'usuarios/activate.html', locals())


class DetailViewRoles(generic.DetailView):
    model = User
    template_name = 'usuarios/usuario_roles.html'
    context_object_name = 'user_detail'

    def get_context_data(self, **kwargs):
        context = super(DetailViewRoles, self).get_context_data(**kwargs)
        user = User.objects.get(pk=self.kwargs['pk'])
        # proyectos = Proyecto.objects.all()
        # rolproyecto_proyecto = RolProyecto_Proyecto.objects.all()
        solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user)
        proyectos_del_usuario = RolProyecto_Proyecto.objects.values('proyecto').distinct()

        todos_los_grupos_del_user = user.groups
        todos_roles_proyecto = RolProyecto.objects.all()

        grupos_del_user = user.groups.all()

        print grupos_del_user

        print todos_roles_proyecto

        lista_roles_pro = []
        for rol_proyecto in todos_roles_proyecto:
            lista_roles_pro.append(rol_proyecto.group)

        lista = []

        for g in grupos_del_user:
            if g not in lista_roles_pro:
                lista.append(g)

        print lista

        context['lista'] = lista
        context['rolesproyecto_list'] = solo_del_usuario
        context['proyectos_list'] = proyectos_del_usuario
        return context

    #@method_decorator(permission_required('usuarios.modificar_usuario'))
    #def dispatch(self, *args, **kwargs):
    #    return super(DetailViewRoles, self).dispatch(*args, **kwargs)


class UserRoles(UpdateView):
    form_class = UserAsignarRolesForm
    template_name = 'usuarios/asignar_rol.html'
    context_object_name = 'user_detail'

    def get_object(self, queryset=None):
        obj = User.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        obj = User.objects.get(pk=self.kwargs['pk'])
        return reverse('usuarios:detail_roles', args=[obj.pk])

    #@method_decorator(permission_required('usuarios.modificar_usuario'))
    #def dispatch(self, *args, **kwargs):
    #    return super(UserRoles, self).dispatch(*args, **kwargs)


#@permission_required('usuarios.modificar_usuario')
@login_required(login_url='/login/')
def user_change_password(request, pk_usuario):
    """
    Funcion que permite modificar el password de un usuario selecionado.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @type pk_usuario: string
    @param pk_usuario: id del usuario con password a modificar

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza usuarios/user_password_change.html para obtener el formulario o
            redirecciona a la vista update del usuario.
    """
    if request.method == 'POST':
        user_detail = get_object_or_404(User, pk=pk_usuario)
        form = MyPasswordChangeForm(user_detail, request.POST)
        if form.is_valid():
            new_user = form.save()
            update_session_auth_hash(request, user_detail)
            return HttpResponseRedirect(reverse('usuarios:update', args=[user_detail.pk]))
    else:
        user_detail = get_object_or_404(User, pk=pk_usuario)
        form = MyPasswordChangeForm(user_detail)

    return render(request, 'usuarios/user_password_change.html', locals())
