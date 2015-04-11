from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse

from models import Proyecto
from django.contrib.auth.models import User, Group
from apps.roles_proyecto.models import RolProyecto, RolProyecto_Proyecto
from forms import AddMiembroForm, ProyectoCreateForm, ProyectoUpdateForm, RolMiembroForm

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de proyectos en el Index
    de la aplicacion Proyecto.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Proyecto
    template_name = 'proyectos/index.html'

    #@method_decorator(permission_required('proyectos.listar_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(IndexView, self).dispatch(*args, **kwargs)
    

class ProyectoCreate(SuccessMessageMixin, CreateView):
    """
    Clase que despliega el formulario para la creacion de proyectos.

    @ivar form_class: Formulario que se utiliza para la creacion de usuarios
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = ProyectoCreateForm
    template_name = 'proyectos/create.html'
    success_message = "%(nombre_corto)s fue creado de manera exitosa"
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.save() Eliminar porque guarda dos veces
        return super(ProyectoCreate, self).form_valid(form)

    def get_success_url(self): 
        return reverse('proyectos:index')

    #@method_decorator(permission_required('proyectos.crear_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(ProyectoCreate, self).dispatch(*args, **kwargs)


class ProyectoUpdate(SuccessMessageMixin, UpdateView):
    """
    Clase que despliega el formulario para la modficacion de proyectos.

    @ivar form_class: Formulario que se utiliza para la modficacion de usuarios
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = ProyectoUpdateForm
    template_name = 'proyectos/update.html'
    success_message = "%(nombre_corto)s ha siso modificado"

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk'])
        return obj

    def get_success_url(self): 
        return reverse('proyectos:index')

    #@method_decorator(permission_required('proyectos.modificar_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(ProyectoUpdate, self).dispatch(*args, **kwargs)

@login_required(login_url='/login/')
#@permission_required('proyectos.eliminar_proyecto')
def eliminar_proyecto(request, pk_proyecto):
    if request.method == 'POST':
        proyecto_detail = get_object_or_404(Proyecto, pk=pk_proyecto)
        proyecto_detail.cancelado = True
        proyecto_detail.save()

        messages.success(request, 'El proyecto fue cancelado con exito.')

        return HttpResponseRedirect('/proyectos/')

    proyecto_detail = get_object_or_404(Proyecto, pk=pk_proyecto)

    return render(request, 'proyectos/delete.html', locals())


@login_required(login_url='/login/')
def proyecto_index(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    template = 'proyectos/proyecto_index.html'

    #Equipo
    lista_equipo = Proyecto.objects.get(pk=pk).equipo.all()
    print lista_equipo
    
    nueva_lista = []
    for u in lista_equipo:
        usu = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, user=u)
        print usu
        nueva_lista.append(usu)

    print nueva_lista

    return render(request, template, locals())


@login_required(login_url='/login/')
#@permission_required('proyectos.asignar_rol_proyecto_proyecto')
def listar_equipo(request, pk_proyecto):
    proyecto = Proyecto.objects.get(pk=pk_proyecto)
    lista_equipo = Proyecto.objects.get(pk=pk_proyecto).equipo.all()
    print lista_equipo
    
    nueva_lista = []
    for u in lista_equipo:
        usu = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, user=u)
        print usu
        nueva_lista.append(usu)

    print nueva_lista
    template = 'proyectos/proyecto_equipo_list.html'
    return render(request, template, locals())


class AddMiembro(generic.UpdateView):
    form_class = AddMiembroForm
    template_name = 'proyectos/proyecto_equipo_add_miembro.html'
    context_object_name = 'proyecto_detail'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse( 'proyectos:equipo_list', args=[obj.pk])

    #@method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(AddMiembro, self).dispatch(*args, **kwargs)


@login_required(login_url='/login/')
@permission_required('proyectos.asignar_rol_proyecto_proyecto')
def delete_miembro(request, pk_proyecto, pk_user):
    template = 'proyectos/proyecto_equipo_delete_miembro.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)
    usuario = get_object_or_404(User, pk=pk_user)
    if request.method == 'POST':

        sm = proyecto.scrum_master.pk

        if sm != usuario.pk:
            proyecto.equipo.remove(usuario)
            lista_roles = RolProyecto_Proyecto.objects.filter(user=usuario, proyecto=proyecto)
            for rol in lista_roles:
                rol.delete()
            return HttpResponseRedirect(reverse( 'proyectos:equipo_list', args=[proyecto.pk]))

        else:
            mensaje = 'No se puede eliminar el usuario ' 
            mensaje =  mensaje + usuario.username + ' del proyecto porque es el Scrum Master. Designe primero como Scrum Master a otro usuario.'
            return render(request, template, locals())

    return render(request, template, locals())


class RolMiembro(UpdateView):
    form_class = RolMiembroForm
    template_name = 'proyectos/proyecto_equipo_rol_miembro.html'
    context_object_name = 'proyecto_detail'

    def get_initial(self):
        initial = super(RolMiembro, self).get_initial()
        user = User.objects.get(pk=self.kwargs['pk_user'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        #las filas con la tupla user_rol_proyecto
        solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        print "solo_del_usuario = %s" % solo_del_usuario
        #listar los roles en ese proyecto
        roles_proyecto_del_usuario = solo_del_usuario.values('rol_proyecto').distinct()
        print "roles_proyecto_del_usuario = %s" % roles_proyecto_del_usuario
        roro = Group.objects.filter(rolproyecto__pk__in=roles_proyecto_del_usuario) 

        print "roro = %s" % roro

        #pasamos los roles del usuario en el proyecto
        initial['rolproyecto'] = roro

        #pasamos el usuario
        initial['user'] = user
        print "user = %s" % user

        return initial

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse( 'proyectos:equipo_list', args=[obj.pk])

    #@method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(RolMiembro, self).dispatch(*args, **kwargs)
