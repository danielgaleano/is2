from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from models import Proyecto
from apps.roles_proyecto.models import RolProyecto_Proyecto
from apps.user_stories.models import UserStory
from apps.sprints.models import Sprint
from apps.flujos.models import Flujo
from forms import AddMiembroForm, ProyectoCreateForm, ProyectoUpdateForm, RolMiembroForm, HorasDeveloperForm


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de proyectos en el Index
    de la aplicacion Proyecto.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    queryset = Proyecto.objects.all().order_by('codigo')
    template_name = 'proyectos/index.html'
    

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

    @method_decorator(permission_required('proyectos.crear_proyecto'))
    def dispatch(self, *args, **kwargs):
        return super(ProyectoCreate, self).dispatch(*args, **kwargs)


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

    @method_decorator(permission_required('proyectos.modificar_proyecto'))
    def dispatch(self, *args, **kwargs):
        return super(ProyectoUpdate, self).dispatch(*args, **kwargs)

@login_required(login_url='/login/')
@permission_required('proyectos.eliminar_proyecto')
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

    duracion_proyecto = proyecto.fecha_fin - proyecto.fecha_inicio
    print "duracion = %s" % duracion_proyecto.days
    duracion = duracion_proyecto.days

    lista_us = UserStory.objects.filter(proyecto=pk).order_by('nombre')[:5]
    lista_sprints = Sprint.objects.filter(proyecto=pk).order_by('pk')
    lista_flujos = Flujo.objects.filter(proyecto=pk).order_by('pk')

    return render(request, template, locals())


@login_required(login_url='/login/')
@permission_required('proyectos.asignar_rol_proyecto_proyecto')
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

    @method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    def dispatch(self, *args, **kwargs):
        return super(AddMiembro, self).dispatch(*args, **kwargs)


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

    @method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    def dispatch(self, *args, **kwargs):
        return super(RolMiembro, self).dispatch(*args, **kwargs)


class HorasDeveloper(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de las horas asignadas a un desarrollador.

    @ivar form_class: Formulario que se utiliza para la asignacion de horas
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = HorasDeveloperForm
    template_name = 'proyectos/proyecto_equipo_horas_developer.html'
    context_object_name = 'proyecto_detail'

    def get_initial(self):
        """
        Metodo que retorna datos iniciales a ser utilizados en el formulario
        @return:
        """
        initial = super(HorasDeveloper, self).get_initial()
        user = User.objects.get(pk=self.kwargs['pk_user'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        #las filas con la tupla user_rol_proyecto
        solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        print "solo_del_usuario = %s" % solo_del_usuario
        rol_developer = []
        for rol in solo_del_usuario:
            if rol.rol_proyecto.group.name == "Developer":
                rol_developer.append(rol)

        print "rol_developer = %s" % rol_developer

        horas = rol_developer[0].horas_developer
        print "rol_developer = %s" % rol_developer

        initial['horas_developer'] = horas
        initial['rol_developer'] = rol_developer
        initial['user'] = user
        print "user = %s" % user

        return initial

    def get_object(self, queryset=None):
        """
        Metodo que retorna el proyecto actual
        @param queryset:
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        """
        Metodo que realiza la redireccion si la modificacion de horas es exitosa
        @return:
        """
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse( 'proyectos:equipo_list', args=[obj.pk])

    def get_context_data(self, **kwargs):
        """
        Metodo que retorna datos a utilizar en el template de la vista
        @param kwargs:
        @return:
        """
        context = super(HorasDeveloper, self).get_context_data(**kwargs)
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        duracion_proyecto = proyecto.fecha_fin - proyecto.fecha_inicio
        #ocho horas por dia
        duracion_horas = duracion_proyecto.days * 8
        print "duracion = %s" % duracion_horas

        context['duracion_horas'] = duracion_horas

        #Usar al determinar la duracion del sprint
        rows_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "rows_del_proyecto = %s" % rows_del_proyecto

        horas_asignadas = 0
        for row in rows_del_proyecto:
            horas_asignadas = horas_asignadas + row.horas_developer

        context['horas_asignadas'] = horas_asignadas

        #self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_user_story'])
        #context['user_story'] = self.user_story
        return context

    @method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    def dispatch(self, *args, **kwargs):
        return super(HorasDeveloper, self).dispatch(*args, **kwargs)
