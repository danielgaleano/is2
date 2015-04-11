from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import Group, User
from forms import RolCreateForm, RolUpdateForm, RolAsignarPermisosForm

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de roles en el Index
    de la aplicacion Roles.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Group
    template_name = 'roles/index.html'


class RolCreate(CreateView):
    """
    Clase que despliega el formulario para la creacion de roles.

    @ivar form_class: Formulario que se utiliza para la creacion de roles
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = RolCreateForm
    template_name = 'roles/create.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save()
        return super(RolCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('roles:index')

    @method_decorator(permission_required('auth.add_group'))
    def dispatch(self, *args, **kwargs):
        return super(RolCreate, self).dispatch(*args, **kwargs)


class RolUpdate(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de roles.

    @ivar form_class: Formulario que se utiliza para la modficacion de roles
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = RolUpdateForm
    template_name = 'roles/update.html'

    def get_object(self, queryset=None):
        obj = Group.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return reverse('roles:index')

    @method_decorator(permission_required('auth.change_group'))
    def dispatch(self, *args, **kwargs):
        return super(RolUpdate, self).dispatch(*args, **kwargs)


@login_required(login_url='/login/')
@permission_required('auth.delete_group')
def eliminar_rol(request, pk_rol):
    if request.method == 'POST':

        rol_detail = get_object_or_404(Group, pk=pk_rol)
        lista_users = User.objects.filter(groups__name=rol_detail.name)

        if len(lista_users) == 0:
            rol_detail.delete()
            return HttpResponseRedirect('/roles/')
        else:
            mensaje = 'No se puede eliminar el rol, porque es utilizado por otro(s) usuario(s): '
            for usuario in lista_users:
                mensaje = mensaje + usuario.username + ', '
            rol_detail = get_object_or_404(Group, pk=pk_rol)
            return render(request, 'roles/delete.html', locals())

    rol_detail = get_object_or_404(Group, pk=pk_rol)

    return render(request, 'roles/delete.html', locals())


class RolPermisos(UpdateView):
    form_class = RolAsignarPermisosForm
    template_name = 'roles/rol_permisos.html'
    context_object_name = 'rol_detail'

    def get_object(self, queryset=None):
        obj = Group.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self):
        return reverse('roles:index')

    @method_decorator(permission_required('auth.change_group'))
    def dispatch(self, *args, **kwargs):
        return super(RolPermisos, self).dispatch(*args, **kwargs)
