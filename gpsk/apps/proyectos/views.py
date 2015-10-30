
from datetime import datetime
#import datetime

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

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

#@permission_required('proyectos.eliminar_proyecto')
@login_required(login_url='/login/')
def eliminar_proyecto(request, pk_proyecto):
    """
    Elimina proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
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
    """
    Redirige al index de Proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    template = 'proyectos/proyecto_index.html'

    lista_equipo = Proyecto.objects.get(pk=pk).equipo.all()
    print lista_equipo
    
    nueva_lista = []
    for u in lista_equipo:
        usu = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, user=u)
        print usu
        nueva_lista.append(usu)

    print nueva_lista

    #duracion_proyecto = proyecto.fecha_fin - proyecto.fecha_inicio
    #print "duracion = %s" % duracion_proyecto.days
    #duracion = duracion_proyecto.days

    duracion = habiles(proyecto.fecha_inicio, proyecto.fecha_fin)


    lista_us = UserStory.objects.filter(proyecto=pk).order_by('nombre')[:5]
    lista_sprints = Sprint.objects.filter(proyecto=pk).order_by('pk')
    lista_flujos = Flujo.objects.filter(proyecto=pk).order_by('pk')

    return render(request, template, locals())


#@permission_required('proyectos.asignar_rol_proyecto_proyecto')
@login_required(login_url='/login/')
def listar_equipo(request, pk_proyecto):
    """
    Lista equipo del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk_proyecto)
    lista_equipo = Proyecto.objects.get(pk=pk_proyecto).equipo.all().order_by('id')
    print lista_equipo

    duracion = habiles(proyecto.fecha_inicio, proyecto.fecha_fin)

    nueva_lista = []
    for u in lista_equipo:
        usu = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, user=u)
        print usu
        nueva_lista.append(usu)

    miembros = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
    horas_hombre_totales = 0
    for miembro in miembros:
        horas_developer_proyecto = 0
        horas_developer_proyecto = miembro.horas_developer * duracion
        horas_hombre_totales = horas_hombre_totales + horas_developer_proyecto

    print nueva_lista
    template = 'proyectos/proyecto_equipo_list.html'
    return render(request, template, locals())


class AddMiembro(generic.UpdateView):
    """
    Clase que despliega el formulario para la agregacion de miembros.

    @ivar form_class: Formulario que se utiliza para la agregacion de usuarios
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
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

#@permission_required('proyectos.asignar_rol_proyecto_proyecto')
@login_required(login_url='/login/')
def delete_miembro(request, pk_proyecto, pk_user):
    """
    Elimina miembro del equipo del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @param pk_user: clave primaria de usuario
    @return: template con texto renderizado
    """
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
    """
    Clase que despliega el template para la especificar los roles de los miembros.

    @ivar form_class: Formulario que se utiliza para la agregacion roles para el usuario
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = RolMiembroForm
    template_name = 'proyectos/proyecto_equipo_rol_miembro.html'
    context_object_name = 'proyecto_detail'

    def get_initial(self):
        initial = super(RolMiembro, self).get_initial()
        user = User.objects.get(pk=self.kwargs['pk_user'])
        proyecto = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        solo_del_usuario = RolProyecto_Proyecto.objects.filter(user=user, proyecto=proyecto)
        print "solo_del_usuario = %s" % solo_del_usuario
        roles_proyecto_del_usuario = solo_del_usuario.values('rol_proyecto').distinct()
        print "roles_proyecto_del_usuario = %s" % roles_proyecto_del_usuario
        roro = Group.objects.filter(rolproyecto__pk__in=roles_proyecto_del_usuario) 

        print "roro = %s" % roro

        initial['rolproyecto'] = roro

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
        #duracion_proyecto = proyecto.fecha_fin - proyecto.fecha_inicio
        duracion_proyecto = habiles(proyecto.fecha_inicio, proyecto.fecha_fin)
        #duracion_horas = duracion_proyecto * 8
        #print "duracion = %s" % duracion_horas

        context['duracion_proyecto'] = duracion_proyecto
        #context['duracion_horas'] = duracion_horas

        rows_del_proyecto = RolProyecto_Proyecto.objects.filter(proyecto=proyecto)
        print "rows_del_proyecto = %s" % rows_del_proyecto

        horas_asignadas = 0
        for row in rows_del_proyecto:
            horas_asignadas = horas_asignadas + row.horas_developer

        context['horas_asignadas'] = horas_asignadas

        return context

    #@method_decorator(permission_required('proyectos.asignar_rol_proyecto_proyecto'))
    #def dispatch(self, *args, **kwargs):
    #    return super(HorasDeveloper, self).dispatch(*args, **kwargs)


#Recibe dos fechas y calcula cuantos dias habiles hay entre las mismas,
#incluyendo la fecha de inicio
def habiles(fecha1, fecha2):

    time1 = int(str(datetime.weekday(fecha1)))
    time2 = int(str(datetime.weekday(fecha2)))
    dia = time1 - time2
    diferencia = fecha2 - fecha1
    valor = int(str(diferencia.days))

    if valor >= 7:
        val = ((valor+dia)//7)*2
        habiles = valor-val+1

        if time1 > 4 or time2 > 4:
            if time2 > time1:
                if time2 == 5:
                    habiles = habiles-1
                else:
                    if time2 == 6:
                        habiles = habiles-2
            else:
                if (time1 > time2 and time1 == 6) and time2 != 5:
                    habiles = habiles+1
                else:
                    if time1 == time2:
                        habiles=habiles-1
    else:
        if (time1+valor) > 5:
            habiles = valor-1
        else:
            if (time1+valor) == 5:
                habiles = valor
            else:
                habiles = valor+1

    return habiles


@login_required(login_url='/login/')
def proyecto_reportes(request, pk):
    """
    Redirige a la vista de reportes del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    template = 'proyectos/proyecto_reportes.html'

    return render(request, template, locals())


@login_required(login_url='/login/')
def proyecto_reporte_trabajos_equipo(request, pk):
    """
    Redirige a la vista de reporte de trabajos por equipo del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_trabajos_equipo_" + proyecto.nombre_corto + ".pdf"

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="%s" ' % pdf_name

    def print_footer_header(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph("GPSK System", styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        date = datetime.now()
        dateFormat = date.strftime("%d-%m-%Y")
        # Footer 1
        footer_1 = Paragraph(dateFormat, styles['Normal'])
        w, h = footer_1.wrap(doc.width, doc.bottomMargin)
        footer_1.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=40,
                            bottomMargin=20,
                            )

    elementos = []
    styles = getSampleStyleSheet()
    header = Paragraph(proyecto.nombre_largo, styles['Heading1'])
    sub_header = Paragraph("User Stories en curso", styles['Heading2'])
    elementos.append(header)
    elementos.append(sub_header)
    headings = ('User Story')
    lista_user_stories = [(p.nombre) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo').filter(estado='Activo')]

    for us in lista_user_stories:
        elementos.append(Paragraph(us, styles['Normal']))
    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_trabajos_equipo_download(request, pk):
    """
    Redirige a la vista de descarga del reporte de trabajos por equipo del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_trabajos_equipo_" + proyecto.nombre_corto + ".pdf"

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s" ' % pdf_name

    def print_footer_header(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()

        # Header
        header = Paragraph("GPSK System", styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

        date = datetime.now()
        dateFormat = date.strftime("%d-%m-%Y")
        # Footer 1
        footer_1 = Paragraph(dateFormat, styles['Normal'])
        w, h = footer_1.wrap(doc.width, doc.bottomMargin)
        footer_1.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    buff = BytesIO()
    doc = SimpleDocTemplate(buff,
                            pagesize=A4,
                            rightMargin=40,
                            leftMargin=40,
                            topMargin=40,
                            bottomMargin=20,
                            )

    elementos = []
    styles = getSampleStyleSheet()
    header = Paragraph(proyecto.nombre_largo, styles['Heading1'])
    sub_header = Paragraph("User Stories en curso", styles['Heading2'])
    elementos.append(header)
    elementos.append(sub_header)
    headings = ('User Story')
    lista_user_stories = [(p.nombre) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo').filter(estado='Activo')]

    for us in lista_user_stories:
        elementos.append(Paragraph(us, styles['Normal']))
    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def iniciar_proyecto(request, pk_proyecto):
    """
    Funcion que realiza la inicializacion del proyecto
    @param request: proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: redirige al index de Proyectos
    """
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)

    proyecto.estado = 'Activo'
    proyecto.fecha_inicio = datetime.now()

    proyecto.save()

    return HttpResponseRedirect(reverse('proyectos:index'))


@login_required(login_url='/login/')
def finalizar_proyecto(request, pk_proyecto):
    """
    Funcion que realiza la finalizacion del proyecto
    @param request: proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: redirige al index de Proyectos
    """
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)

    template = 'proyectos/proyecto_finalizar.html'
    proyecto = get_object_or_404(Proyecto, pk=pk_proyecto)

    sprints = Sprint.objects.filter(proyecto=proyecto, estado='Activo')

    if request.method == 'POST':

        proyecto.estado = 'Finalizado'
        print "fecha = %s" % datetime.date.today()
        proyecto.fecha_fin = datetime.date.today()

        proyecto.save()

        for sprint in sprints:
            sprint.estado = 'Finalizado'
            sprint.fecha_fin = datetime.date.today()

            user_stories = UserStory.objects.filter(sprint=sprint, estado='Activo')

            for us in user_stories:
                us.estado = 'Pendiente'
                us.save()

            sprint.save()

        return HttpResponseRedirect(reverse('proyectos:index', args=[pk_proyecto]))
    if sprints:
        mensaje = 'Existen sprints que no han finalizado.'

    return render(request, template, locals())
