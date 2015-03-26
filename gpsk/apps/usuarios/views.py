from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import UpdateView
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from forms import UserCreateForm, UserUpdateForm
from django.views.generic.edit import FormView

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


class UserIndexView(generic.ListView):
    """
    Clase que despliega la lista completa de usuarios en el Index
    de la aplicacion Usuarios.

    @ivar model: Modelo que se utiliza para generar la lista
    @type model: django.contrib.auth.models

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = User
    template_name = 'usuarios/index.html'


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


@login_required(login_url='/login/')
def eliminar_usuario(request, pk_usuario):
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
