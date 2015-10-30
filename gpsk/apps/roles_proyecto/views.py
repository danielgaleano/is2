from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import UpdateView, FormView
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from forms import RolProyectoCreateForm, RolProyectoUpdateForm, RolProyectoPermisosForm


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de roles de proyectos en el Index
    de la aplicacion Roles_Proyecto.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    #model = Group
    template_name = 'roles_proyecto/index.html'

    def get_queryset(self):

        return Group.objects.all().order_by('pk')

    #@method_decorator(permission_required('roles_proyecto.listar_rolproyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(IndexView, self).dispatch(*args, **kwargs)


class RolCreate(FormView):
    """
    Clase que despliega el formulario para la creacion de roles de proyectos.

    @ivar form_class: Formulario que se utiliza para la creacion de roles de proyecto
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = RolProyectoCreateForm
    template_name = 'roles_proyecto/create.html'
    # success_url = '/thanks/'
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.save()
        return super(RolCreate, self).form_valid(form)

    def get_success_url(self): 
        return reverse('roles_proyecto:index')

    @method_decorator(permission_required('roles_proyecto.crear_rolproyecto'))
    def dispatch(self, *args, **kwargs):
        return super(RolCreate, self).dispatch(*args, **kwargs)

    
class RolUpdate(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de roles de proyectos.

    @ivar form_class: Formulario que se utiliza para la modficacion de roles
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = RolProyectoUpdateForm
    template_name = 'roles_proyecto/update.html'
    context_object_name = 'rol_detail'

    def get_object(self, queryset=None):
        obj = Group.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self): 
        return reverse( 'roles_proyecto:index')

    @method_decorator(permission_required('roles_proyecto.modificar_rolproyecto'))
    def dispatch(self, *args, **kwargs):
        return super(RolUpdate, self).dispatch(*args, **kwargs)



@login_required(login_url='/login/')
@permission_required('roles_proyecto.eliminar_rolproyecto')
def eliminar_rol(request, pk_rol):
    if request.method == 'POST':

        rol_detail = get_object_or_404(Group, pk=pk_rol)
        lista_users = User.objects.filter(groups__name=rol_detail.name)

        if len(lista_users) == 0:
            rol_detail.delete()
            return HttpResponseRedirect('/roles_proyecto/')
        else:
            mensaje = 'No se puede eliminar el rol, porque es utilizado por otro(s) usuario(s): '
            for usuario in lista_users:
                mensaje = mensaje + usuario.username + ', '
            rol_detail = get_object_or_404(Group, pk=pk_rol)
            return render(request, 'roles_proyecto/delete.html', locals())


    rol_detail = get_object_or_404(Group, pk=pk_rol)
    
    return render(request, 'roles_proyecto/delete.html', locals())


class RolPermisos(UpdateView):
    form_class = RolProyectoPermisosForm
    template_name = 'roles_proyecto/rol_proyecto_permisos.html'
    context_object_name = 'rol_detail'

    def get_object(self, queryset=None):
        obj = Group.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self): 
        return reverse( 'roles_proyecto:index')

    @method_decorator(permission_required('roles_proyecto.modificar_rolproyecto'))
    def dispatch(self, *args, **kwargs):
        return super(RolPermisos, self).dispatch(*args, **kwargs)
