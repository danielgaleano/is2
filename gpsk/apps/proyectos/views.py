import json
from datetime import datetime
import datetime as datetime2
from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.legends import Legend

from models import Proyecto
from apps.roles_proyecto.models import RolProyecto_Proyecto, RolProyecto
from apps.user_stories.models import UserStory, HistorialUserStory, Tarea
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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("User Stories en curso", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)
    headings = ('User Story')
    lista_user_stories = [(p.nombre, p.descripcion, p.usuario) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo').filter(estado='Activo')]
    print "lista_user_Stories %s" % lista_user_stories
    #lista_us = []
    #for us in lista_user_stories:
    #    elementos.append(Paragraph(us, styles['Normal']))

    headings = ('User Story', 'Descripcion', 'Responsable')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen)
        ]
    ))

    elementos.append(t)

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("User Stories en curso", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)
    headings = ('User Story')
    lista_user_stories = [(p.nombre, p.descripcion, p.usuario) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo').filter(estado='Activo')]
    print "lista_user_Stories %s" % lista_user_stories
    #lista_us = []
    #for us in lista_user_stories:
    #    elementos.append(Paragraph(us, styles['Normal']))

    headings = ('User Story', 'Descripcion', 'Responsable')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (3, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen)
        ]
    ))

    elementos.append(t)

    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def reporte_grafico_reportlab(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_grafico_sprints_" + proyecto.nombre_corto + ".pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="%s" ' % pdf_name

    p = canvas.Canvas(response)

    titulo = "Burndown chart de los sprints de %s." % proyecto.nombre_corto

    p.drawString(180, 800, titulo)

    sprints = Sprint.objects.filter(proyecto=proyecto).exclude(estado='No iniciado').order_by('fecha_inicio')

    lista_calculado_json = []

    for sprint in sprints:
        user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado')

        duracion = sprint.duracion

        lista_tareas_us_sprint = Tarea.objects.filter(sprint=sprint, tipo='Registro de Tarea')
        horas_totales_acumuladas = 0
        for tarea in lista_tareas_us_sprint:
            horas_totales_acumuladas = horas_totales_acumuladas + tarea.horas_de_trabajo

        horas_calculadas_chart = 0

        user_stories_lista = []

        lista_data = []
        horas_totales_estimacion = 0
        for us in user_stories:
            #fecha = str(us.fecha)

            horas_totales_estimacion = horas_totales_estimacion + us.estimacion

            user_stories_lista.append({'year': us.nombre, 'value': us.estimacion})

        user_stories_json = json.dumps(user_stories_lista)
        print "horas_tot_ estimacion %s" % horas_totales_estimacion
        calculado = horas_totales_estimacion
        calculado2 = horas_totales_estimacion


        rol_developer = RolProyecto.objects.get(group__name='Developer')
        lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
        cantidad_developers = lista_developers.count()

        horas_totales_sprint = 0
        horas_developers_sprint_dia = 0
        for miembro in lista_developers:
            horas_developers_sprint_dia = horas_developers_sprint_dia + miembro.horas_developer
            #horas_totales_sprint = horas_totales_sprint + horas_developer_sprint


        #while tarea.fecha.date() <= sprint.fecha_fin:
        #    pass
        #for dia in range(1, duracion+1):
        day = 0
        dia = 1
        lista_data.append({'year': 0, 'value2': calculado2, 'value': calculado})

        la_data_a = []
        la_data_b = []
        la_data_dias = []
        la_data_a.append(calculado2)
        la_data_b.append(calculado)
        la_data_dias.append("Dia 0")

        print "antes while"
        while sprint.fecha_inicio+datetime2.timedelta(days=day) <= sprint.fecha_fin:
            print "fecha days = %s" % str(sprint.fecha_inicio+datetime2.timedelta(days=day))
            print "fecha_fin = %s" % sprint.fecha_fin

            print "Dia %s" % dia
            print "calculado = %s" % calculado
            print "calculado2 = %s" % calculado2
            #calculado = horas_totales_estimacion
            #entro = False

            if sprint.fecha_inicio+datetime2.timedelta(days=day) <= datetime2.date.today():
                for tarea in lista_tareas_us_sprint:

                    print "tareafecha %s, sprint_inicio %s" % (tarea.fecha, sprint.fecha_inicio)
                    if tarea.fecha.date() == sprint.fecha_inicio+datetime2.timedelta(days=day):
                        #entro = True
                        print "if"
                        print "estado %s" % tarea.user_story.estado
                        if calculado - tarea.horas_de_trabajo >= 0:
                            calculado = calculado - tarea.horas_de_trabajo

                        else:
                            calculado = 0

                            #aqui se podria agregar que si la resta es menor a cero
                            #asignarle cero para que la linea de trabajo realizado no sea negativa
                            #se deberia ver tambien si se termina antes de la fecha de finalizacion esperada
                            #la linea de trabajo realizado deberia teminar alli

                        print "calculado = %s" % calculado
            else:
                calculado = None

            #if entro:
            dia_semana = (sprint.fecha_inicio+datetime2.timedelta(days=day)).weekday()
            print "dia_semana %s" % dia_semana
            if dia_semana < 5:
                calculado2 = calculado2 - horas_developers_sprint_dia
                print "calculado2 = %s" % calculado2
                lista_data.append({'year': dia, 'value2': calculado2, 'value': calculado})
                dia = dia + 1

                la_data_a.append(calculado2)
                la_data_b.append(calculado)
                el_dia = "Dia %s" % (dia-1)
                la_data_dias.append(el_dia)

            day = day + 1

        calculado_json = json.dumps(lista_data)
        #print "calculado_json" % str(calculado_json)
        print lista_data

        lista_calculado_json.append(calculado_json)

        # Se despliega el grafico con sus datos
        j = 750
        p.setFont('Helvetica', 12)
        p.drawString(220, 780, sprint.nombre + ': ' + sprint.estado)

        data = [la_data_a,la_data_b]

        drawing = Drawing(450, 200)

        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 200
        lc.width = 400
        lc.data = data
        lc.joinedLines = 1
        lc.categoryAxis.categoryNames = la_data_dias
        lc.categoryAxis.labels.boxAnchor = 'n'
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = horas_totales_estimacion + 40
        lc.valueAxis.valueStep = 40
        lc.lines.symbol = makeMarker('Circle')
        lc.lines[0].strokeWidth = 1.5
        lc.lines[1].strokeWidth = 1.5
        lc.categoryAxis.labels.angle = 30
        lc.categoryAxis.labels.fontSize = 8

        ley = Legend()
        ley.alignment = 'right'
        ley.x = 80
        ley.y = 10
        ley.deltax = 60
        ley.dxTextSpace = 10
        ley.columnMaximum = 4
        items = [(colors.red, "Tiempo estimado"), (colors.green, "Tiempo real")]
        ley.colorNamePairs = items

        drawing.add(ley)

        drawing.add(lc)

        renderPDF.draw(drawing, p, 50, 500)

        p.showPage()

    p.save()

    return response


@login_required(login_url='/login/')
def reporte_grafico_reportlab_download(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_grafico_sprints_" + proyecto.nombre_corto + ".pdf"

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s" ' % pdf_name

    p = canvas.Canvas(response)
    titulo = "Burndown chart de los sprints de %s." % proyecto.nombre_corto

    p.drawString(180, 800, titulo)

    sprints = Sprint.objects.filter(proyecto=proyecto).exclude(estado='No iniciado').order_by('fecha_inicio')

    lista_calculado_json = []

    for sprint in sprints:
        user_stories = UserStory.objects.filter(sprint=sprint).exclude(estado='Descartado')

        duracion = sprint.duracion

        lista_tareas_us_sprint = Tarea.objects.filter(sprint=sprint, tipo='Registro de Tarea')
        horas_totales_acumuladas = 0
        for tarea in lista_tareas_us_sprint:
            horas_totales_acumuladas = horas_totales_acumuladas + tarea.horas_de_trabajo

        horas_calculadas_chart = 0

        user_stories_lista = []

        lista_data = []
        horas_totales_estimacion = 0
        for us in user_stories:
            #fecha = str(us.fecha)

            horas_totales_estimacion = horas_totales_estimacion + us.estimacion

            user_stories_lista.append({'year': us.nombre, 'value': us.estimacion})

        user_stories_json = json.dumps(user_stories_lista)
        print "horas_tot_ estimacion %s" % horas_totales_estimacion
        calculado = horas_totales_estimacion
        calculado2 = horas_totales_estimacion


        rol_developer = RolProyecto.objects.get(group__name='Developer')
        lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
        cantidad_developers = lista_developers.count()

        horas_totales_sprint = 0
        horas_developers_sprint_dia = 0
        for miembro in lista_developers:
            horas_developers_sprint_dia = horas_developers_sprint_dia + miembro.horas_developer
            #horas_totales_sprint = horas_totales_sprint + horas_developer_sprint


        #while tarea.fecha.date() <= sprint.fecha_fin:
        #    pass
        #for dia in range(1, duracion+1):
        day = 0
        dia = 1
        lista_data.append({'year': 0, 'value2': calculado2, 'value': calculado})

        la_data_a = []
        la_data_b = []
        la_data_dias = []
        la_data_a.append(calculado2)
        la_data_b.append(calculado)
        la_data_dias.append("Dia 0")

        print "antes while"
        while sprint.fecha_inicio+datetime2.timedelta(days=day) <= sprint.fecha_fin:
            print "fecha days = %s" % str(sprint.fecha_inicio+datetime2.timedelta(days=day))
            print "fecha_fin = %s" % sprint.fecha_fin

            print "Dia %s" % dia
            print "calculado = %s" % calculado
            print "calculado2 = %s" % calculado2
            #calculado = horas_totales_estimacion
            #entro = False

            if sprint.fecha_inicio+datetime.timedelta(days=day) <= datetime.date.today():
                for tarea in lista_tareas_us_sprint:

                    print "tareafecha %s, sprint_inicio %s" % (tarea.fecha, sprint.fecha_inicio)
                    if tarea.fecha.date() == sprint.fecha_inicio+datetime2.timedelta(days=day):
                        #entro = True
                        print "if"
                        print "estado %s" % tarea.user_story.estado
                        if calculado - tarea.horas_de_trabajo >= 0:
                            calculado = calculado - tarea.horas_de_trabajo

                        else:
                            calculado = 0

                            #aqui se podria agregar que si la resta es menor a cero
                            #asignarle cero para que la linea de trabajo realizado no sea negativa
                            #se deberia ver tambien si se termina antes de la fecha de finalizacion esperada
                            #la linea de trabajo realizado deberia teminar alli

                        print "calculado = %s" % calculado
            else:
                calculado = None

            #if entro:
            dia_semana = (sprint.fecha_inicio+datetime2.timedelta(days=day)).weekday()
            print "dia_semana %s" % dia_semana
            if dia_semana < 5:
                calculado2 = calculado2 - horas_developers_sprint_dia
                print "calculado2 = %s" % calculado2
                lista_data.append({'year': dia, 'value2': calculado2, 'value': calculado})
                dia = dia + 1

                la_data_a.append(calculado2)
                la_data_b.append(calculado)
                el_dia = "Dia %s" % (dia-1)
                la_data_dias.append(el_dia)

            day = day + 1

        calculado_json = json.dumps(lista_data)
        #print "calculado_json" % str(calculado_json)
        print lista_data

        lista_calculado_json.append(calculado_json)

        # Se despliega el grafico con sus datos
        j = 750
        p.setFont('Helvetica', 12)
        p.drawString(220, 780, sprint.nombre + ': ' + sprint.estado)

        data = [la_data_a,la_data_b]

        drawing = Drawing(450, 200)

        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 200
        lc.width = 400
        lc.data = data
        lc.joinedLines = 1
        lc.categoryAxis.categoryNames = la_data_dias
        lc.categoryAxis.labels.boxAnchor = 'n'
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = horas_totales_estimacion + 40
        lc.valueAxis.valueStep = 40
        lc.lines.symbol = makeMarker('Circle')
        lc.lines[0].strokeWidth = 1.5
        lc.lines[1].strokeWidth = 1.5
        lc.categoryAxis.labels.angle = 30
        lc.categoryAxis.labels.fontSize = 8

        ley = Legend()
        ley.alignment = 'right'
        ley.x = 80
        ley.y = 10
        ley.deltax = 60
        ley.dxTextSpace = 10
        ley.columnMaximum = 4
        items = [(colors.red, "Tiempo estimado"), (colors.green, "Tiempo real")]
        ley.colorNamePairs = items

        drawing.add(ley)

        drawing.add(lc)

        renderPDF.draw(drawing, p, 50, 500)

        p.showPage()

    p.save()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_trabajos_usuario(request, pk):
    """
    Redirige a la vista de reporte de trabajos por usuario del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_trabajos_usuario_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("User Stories por usuario", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)
    #headings = ('User Story')

    rol_developer = RolProyecto.objects.get(group__name='Developer')
    lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
    cantidad_developers = lista_developers.count()

    print lista_developers

    lista_usuarios = []
    lista_total = []
    for dev in lista_developers:
        lista_usuarios = [(p.nombre, p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).filter(usuario=dev.user).order_by('sprint')]
        lista_total = lista_total + lista_usuarios

        nombre_usuario = dev.user.username
        el_nombre = nombre_usuario
        #el_nombre = Paragraph(nombre_usuario, styles['Normal'])
        #elementos.append(el_nombre)

        header_nombre = (el_nombre, '', '')
        headings = ('User story', 'Flujo', 'Estado')
        t = Table([header_nombre]+ [headings] + lista_usuarios)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (4, -1), 1, colors.limegreen),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
                ('BACKGROUND', (0, 1), (-1, 1), colors.limegreen),
                ('SPAN',(0,0),(-1,0)),
            ]
        ))
        elementos.append(t)
        espacio = Spacer(1, 10)
        elementos.append(espacio)

    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_trabajos_usuario_download(request, pk):
    """
    Redirige a la vista de reporte de trabajos por usuario del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_trabajos_usuario_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("User Stories por usuario", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)
    #headings = ('User Story')

    rol_developer = RolProyecto.objects.get(group__name='Developer')
    lista_developers = RolProyecto_Proyecto.objects.filter(proyecto=proyecto, rol_proyecto=rol_developer).order_by('id')
    cantidad_developers = lista_developers.count()

    print lista_developers

    lista_usuarios = []
    lista_total = []
    for dev in lista_developers:
        lista_usuarios = [(p.nombre, p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).filter(usuario=dev.user).order_by('sprint')]
        lista_total = lista_total + lista_usuarios

        nombre_usuario = dev.user.username
        el_nombre = nombre_usuario
        #el_nombre = Paragraph(nombre_usuario, styles['Normal'])
        #elementos.append(el_nombre)

        header_nombre = (el_nombre, '', '')
        headings = ('User story', 'Flujo', 'Estado')
        t = Table([header_nombre]+ [headings] + lista_usuarios)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (4, -1), 1, colors.limegreen),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
                ('BACKGROUND', (0, 1), (-1, 1), colors.limegreen),
                ('SPAN',(0,0),(-1,0)),
            ]
        ))
        elementos.append(t)
        espacio = Spacer(1, 10)
        elementos.append(espacio)

    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_actividades(request, pk):
    """
    Redirige a la vista de reporte de actividades del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_actividades_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("Lista de actividades", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)

    lista_flujos = Flujo.objects.filter(proyecto=pk).order_by('nombre')

    for flujo in lista_flujos:
        query = Flujo.objects.get(pk=flujo.pk)
        print(query)
        lista_actividades = [(p.orden, p.nombre,) for p in Flujo.objects.get(pk=flujo.pk).actividades.all().order_by('orden')]

        print(lista_actividades)
        nombre_flujo = flujo.nombre
        el_nombre = nombre_flujo

        header_nombre = ('Flujo: ' + el_nombre,)
        headings = ('', 'Actividades',)
        t = Table([header_nombre]+ [headings] + lista_actividades)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (4, -1), 1, colors.limegreen),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
                ('BACKGROUND', (0, 1), (-1, 1), colors.limegreen),
                ('SPAN',(0,0),(-1,0)),
            ]
        ))
        elementos.append(t)
        espacio = Spacer(1, 10)
        elementos.append(espacio)

    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_actividades_download(request, pk):
    """
    Redirige a la vista de reporte de actividades del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_actividades_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("Lista de actividades", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)

    lista_flujos = Flujo.objects.filter(proyecto=pk).order_by('nombre')

    for flujo in lista_flujos:
        query = Flujo.objects.get(pk=flujo.pk)
        print(query)
        lista_actividades = [(p.orden, p.nombre,) for p in Flujo.objects.get(pk=flujo.pk).actividades.all().order_by('orden')]

        print(lista_actividades)
        nombre_flujo = flujo.nombre
        el_nombre = nombre_flujo

        header_nombre = ('Flujo: ' + el_nombre,)
        headings = ('', 'Actividades',)
        t = Table([header_nombre]+ [headings] + lista_actividades)
        t.setStyle(TableStyle(
            [
                ('GRID', (0, 0), (4, -1), 1, colors.limegreen),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
                ('BACKGROUND', (0, 1), (-1, 1), colors.limegreen),
                ('SPAN',(0,0),(-1,0)),
            ]
        ))
        elementos.append(t)
        espacio = Spacer(1, 10)
        elementos.append(espacio)

    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_product_backlog(request, pk):
    """
    Redirige a la vista de reporte del Product Backlog del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_product_backlog_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("Product backlog", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)

    lista_user_stories = [(p.nombre, p.prioridad, p.estimacion,  p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).order_by('-prioridad')]

    headings = ('Nombre', 'Prioridad', 'Estimacion', 'Flujo', 'Estado')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen),

        ]
    ))
    elementos.append(t)


    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_product_backlog_download(request, pk):
    """
    Redirige a la vista de reporte del Product Backlog del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_product_backlog_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])
    sub_header = Paragraph("Product backlog", styles['Title'])
    elementos.append(header)
    elementos.append(sub_header)

    lista_user_stories = [(p.nombre, p.prioridad, p.estimacion,  p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).order_by('-prioridad')]

    headings = ('Nombre', 'Prioridad', 'Estimacion', 'Flujo', 'Estado')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen),

        ]
    ))
    elementos.append(t)


    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_sprint_backlog(request, pk):
    """
    Redirige a la vista de reporte del Sprint Backlog del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_sprint_backlog_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])

    sprint = Sprint.objects.filter(estado='Activo')
    sprint_title = Paragraph(sprint[0].nombre, styles['Title'])

    sub_header = Paragraph("Sprint backlog", styles['Title'])
    elementos.append(header)
    elementos.append(sprint_title)
    elementos.append(sub_header)




    lista_user_stories = [(p.nombre, p.prioridad, p.estimacion, p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo')]
    # lista_user_stories = [(p.nombre, p.prioridad, p.estimacion,  p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).order_by('-prioridad')]

    headings = ('Nombre', 'Prioridad', 'Estimacion', 'Flujo', 'Estado')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen),

        ]
    ))
    elementos.append(t)


    doc.build(elementos, onFirstPage=print_footer_header, onLaterPages=print_footer_header)
    response.write(buff.getvalue())
    buff.close()

    return response


@login_required(login_url='/login/')
def proyecto_reporte_sprint_backlog_download(request, pk):
    """
    Redirige a la vista de reporte del Sprint Backlog del proyecto
    @param request: Proyecto
    @param pk_proyecto: clave primaria de proyecto
    @return: template con texto renderizado
    """
    proyecto = Proyecto.objects.get(pk=pk)
    pdf_name = "reporte_sprint_backlog_" + proyecto.nombre_corto + ".pdf"

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
    header = Paragraph(proyecto.nombre_largo, styles['Title'])

    sprint = Sprint.objects.filter(estado='Activo')
    sprint_title = Paragraph(sprint[0].nombre, styles['Title'])

    sub_header = Paragraph("Sprint backlog", styles['Title'])
    elementos.append(header)
    elementos.append(sprint_title)
    elementos.append(sub_header)




    lista_user_stories = [(p.nombre, p.prioridad, p.estimacion, p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).filter(sprint__estado='Activo')]
    # lista_user_stories = [(p.nombre, p.prioridad, p.estimacion,  p.flujo, p.estado) for p in UserStory.objects.filter(proyecto=pk).order_by('-prioridad')]

    headings = ('Nombre', 'Prioridad', 'Estimacion', 'Flujo', 'Estado')
    t = Table([headings] + lista_user_stories)
    t.setStyle(TableStyle(
        [
            ('GRID', (0, 0), (-1, -1), 1, colors.limegreen),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkgreen),
            ('BACKGROUND', (0, 0), (-1, 0), colors.limegreen),

        ]
    ))
    elementos.append(t)


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

    usuario = request.user

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

                historial_us = HistorialUserStory(user_story=us, operacion='modificado', campo="estado",
                                                  valor='Pendiente', usuario=usuario)
                historial_us.save()

            sprint.save()

        return HttpResponseRedirect(reverse('proyectos:index', args=[pk_proyecto]))
    if sprints:
        mensaje = 'Existen sprints que no han finalizado.'

    return render(request, template, locals())


class ProyectoVer(generic.DetailView):

    model = Proyecto

    template_name = 'proyectos/ver.html'
