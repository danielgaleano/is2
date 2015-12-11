from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission

from apps.proyectos.models import Proyecto
from apps.roles_proyecto.models import RolProyecto_Proyecto
from forms import PlantillaFlujoCreateForm, ActividadCreateForm, AsignarFlujoProyectoForm, FlujoCreateForm
from models import Flujo, ActividadFlujo, ActividadFlujoPlantilla, Estado, PlantillaFlujo


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de flujos en el Index
    de la aplicacion Proyecto.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    queryset = PlantillaFlujo.objects.all().order_by('nombre')
    template_name = 'flujos/index.html'


class FlujoCreate(CreateView):
    """
    Clase que despliega el formulario para la creacion de flujos.

    @ivar form_class: Formulario que se utiliza para la creacion de flujos
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = FlujoCreateForm
    template_name = 'flujos/create.html'

    def form_valid(self, form):
        return super(FlujoCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse( 'flujos:index')


class PlantillaFlujoCreate(CreateView):
    """
    Clase que despliega el formulario para la creacion de plantillas de flujos.

    @ivar form_class: Formulario que se utiliza para la creacion de plantillas de flujos
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = PlantillaFlujoCreateForm
    template_name = 'flujos/create.html'

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
        return super(PlantillaFlujoCreate, self).form_valid(form)

    def get_success_url(self):
        """
        Metodo que redirecciona al index de plantillas de flujo una vez que el formulario se haya guardado correctamente.

        @type self: FormView
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion flujos
        """
        return reverse('flujos:index')

@csrf_exempt
def prueba(request):
    if request.is_ajax():
        el_nombre_plantilla = request.POST.get('nombre_plantilla')
        plantilla = PlantillaFlujo(nombre=el_nombre_plantilla)
        plantilla.save()

        print "plantilla= %s" % el_nombre_plantilla
        print plantilla

    return render(request, 'flujos/create_ajax.html', locals())

@csrf_exempt
def crear_plantilla_flujo(request):
    """
    Funcion que crea una plantilla de flujo.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza flujos/create_ajax.html para obtener el formulario y
            redirecciona a la vista index de plantillas de flujo si fue creado con exito.
    """
    slide_list = ActividadFlujo.objects.all()
    active = []
    inactive = []

    lista_flujo_act = []

    for slide in slide_list:
        active.append(slide)
    if request.is_ajax():
        print("POST")



        def clean_id_list(id_list):
            clean_id_list = []
            for item in id_list:
                try:
                    clean_id_list.append(int(item))
                except ValueError:
                    pass
            return clean_id_list

        def update_slides(id_list, active, trash=False):

            nombre_plantilla = request.POST.get('nombre_plantilla')

            print "nombre_plan= %s" % nombre_plantilla


            try:
                pl = PlantillaFlujo.objects.get(nombre=nombre_plantilla)
                existe = True
            except ObjectDoesNotExist:
                existe = False
            if existe:
                error = True
                mensaje_error_repetido = 'Ya existe una plantilla de flujo ese nombre, escriba otro nombre.'
                return error
            else:
                error = False

            if error==False:
                plantilla = PlantillaFlujo(nombre=nombre_plantilla)
                plantilla.save()

                print id_list
                clean_ids = clean_id_list(id_list)
                print clean_ids
                #slides = Actividad.objects.filter(pk__in=clean_ids)
                slides = clean_ids
                print slides

                #lista_flujo_act = []

                for ele in slides:
                    act = ActividadFlujo.objects.get(pk=int(ele))
                    nueva_actividad_flujo = ActividadFlujoPlantilla.objects.create(nombre=act.nombre, orden=act.orden)

                    estado1 = Estado(nombre="To do")
                    estado1.save()
                    estado2 = Estado(nombre="Doing")
                    estado2.save()
                    estado3 = Estado(nombre="Done")
                    estado3.save()

                    nueva_actividad_flujo.estados.add(estado1)
                    nueva_actividad_flujo.estados.add(estado2)
                    nueva_actividad_flujo.estados.add(estado3)
                    nueva_actividad_flujo.save()

                    lista_flujo_act.append(nueva_actividad_flujo)
                    print lista_flujo_act

                sorting_counter = 1
                print "Hola"
                for slide_obj in lista_flujo_act:
                    #slide = Actividad.objects.get(pk=int(slide_obj))
                    actividadFlujo = ActividadFlujoPlantilla.objects.get(pk=slide_obj.pk)

                    #print slide.orden
                    if trash:
                        print "IF"
                        # While this is fine for my requirements, you may want
                        # to check permissions here (I have @login_required)
                        actividadFlujo.delete()
                    else:
                        print "Else"
                        actividadFlujo.orden = sorting_counter
                        #slide.active = active
                        actividadFlujo.save()
                        sorting_counter += 1

                    plantilla.actividades.add(actividadFlujo)
                    plantilla.save()
                print "plantilla %s" % plantilla
                return error


        if 'inactive' in request.POST:
            inactive_list = request.POST.getlist('actividad[]')
            print 'inactive_list: %s :' % inactive_list
            print "request %s" % request.POST
            resultado = update_slides(inactive_list, active=False)
            print "Resultado= %s" % resultado
            if resultado:
                mensaje_error_repetido = 'Ya existe una plantilla de flujo ese nombre, escriba otro nombre.'
                print "mensaje= %s" % mensaje_error_repetido
                return render(request, 'flujos/create_ajax.html', locals())






        print "en views %s" % lista_flujo_act
        # form = PlantillaFlujoCreateForm(request.POST, lista=lista_flujo_act)

        # if form.is_valid():
            #for act in inactive:

        #    form.save()

        #    return HttpResponseRedirect(reverse('flujos:index'))



    #else:

        # form = PlantillaFlujoCreateForm()


    return render(request, 'flujos/create_ajax.html', locals())


@csrf_exempt
def editar_plantilla_flujo(request, pk_plantilla_flujo):
    slide_list = ActividadFlujo.objects.all()
    active = []
    inactive = []
    inactive_clean = []
    inactive_nombres = []


    lista_flujo_act = []

    plantilla_flujo = PlantillaFlujo.objects.get(pk=pk_plantilla_flujo)
    nombre_plantilla = plantilla_flujo.nombre
    lista_actividades_plantilla = plantilla_flujo.actividades.all().order_by('orden')

    print "lista= %s" % lista_actividades_plantilla

    for a in lista_actividades_plantilla:
        inactive.append(a)
        inactive_clean.append(a.pk)
        inactive_nombres.append(a.nombre)

    print "inactive= %s" % inactive
    print "inactive_clean= %s" % inactive_clean
    print "slide_list= %s" % slide_list


    lista_nombre_plantilla_flujo = []
    for i in slide_list:
        lista_nombre_plantilla_flujo.append(i.nombre)

    print "lista_nombre_plantilla_flujo = %s" % lista_nombre_plantilla_flujo

    for i in lista_nombre_plantilla_flujo:
        if i not in inactive_nombres:
            active.append(ActividadFlujo.objects.get(nombre=i))


    #for slide in slide_list:
    #    print "slide= %s" % slide.orden
    #    active.append(slide)

    if request.is_ajax():
        print("POST")


        def clean_id_list(id_list):
            clean_id_list = []
            for item in id_list:
                print "item= %s" % item
                try:
                    clean_id_list.append(int(item))
                except ValueError:
                    pass
            return clean_id_list

        #inactive_clean = clean_id_list(inactive)

        def update_slides(id_list, active, trash=False):

            nombre_plantilla = request.POST.get('nombre_plantilla')

            print "nombre_plan= %s" % nombre_plantilla


            try:
                pl = PlantillaFlujo.objects.get(nombre=nombre_plantilla)
                if pl.pk == plantilla_flujo.pk:
                    existe = False
                else:
                    existe = True
            except ObjectDoesNotExist:
                existe = False
            if existe:
                error = True
                mensaje_error_repetido = 'Ya existe una plantilla de flujo ese nombre, escriba otro nombre.'
                return error
            else:
                error = False

            # nombre_plantilla = request.POST.get('nombre_plantilla')
            # plantilla_flujo.nombre = nombre_plantilla
            #plantilla_flujo = PlantillaFlujo(nombre=nombre_plantilla)
            # plantilla_flujo.save()

            if error==False:

                plantilla_flujo.nombre = nombre_plantilla
                plantilla_flujo.save()

                print id_list
                clean_ids = clean_id_list(id_list)
                print clean_ids
                #slides = Actividad.objects.filter(pk__in=clean_ids)
                slides = clean_ids
                print slides

                #lista_flujo_act = []

                for ele in slides:
                    print "ele = %s" % ele
                    if ele not in inactive_clean:
                        act = ActividadFlujo.objects.get(pk=int(ele))
                        #act = ActividadFlujo.objects.get(nombre=)
                        nueva_actividad_flujo = ActividadFlujoPlantilla.objects.create(nombre=act.nombre, orden=act.orden)

                        estado1 = Estado(nombre="To do")
                        estado1.save()
                        estado2 = Estado(nombre="Doing")
                        estado2.save()
                        estado3 = Estado(nombre="Done")
                        estado3.save()

                        nueva_actividad_flujo.estados.add(estado1)
                        nueva_actividad_flujo.estados.add(estado2)
                        nueva_actividad_flujo.estados.add(estado3)
                        nueva_actividad_flujo.save()

                        lista_flujo_act.append(nueva_actividad_flujo)
                        print lista_flujo_act

                    else:
                        acti = ActividadFlujoPlantilla.objects.get(pk=int(ele))
                        acti.save()
                        lista_flujo_act.append(acti)

                sorting_counter = 1
                print "Hola"
                for slide_obj in lista_flujo_act:
                    #slide = Actividad.objects.get(pk=int(slide_obj))
                    actividadFlujo = ActividadFlujoPlantilla.objects.get(pk=slide_obj.pk)

                    #print slide.orden
                    if trash:
                        print "IF"
                        # While this is fine for my requirements, you may want
                        # to check permissions here (I have @login_required)
                        actividadFlujo.delete()
                    else:
                        print "Else"
                        actividadFlujo.orden = sorting_counter
                        #slide.active = active
                        actividadFlujo.save()
                        sorting_counter += 1

                    todas_act_plantilla = plantilla_flujo.actividades.all()

                #    if int(slide_obj.pk) not in inactive_clean:
                #        print "slide_obj= %s" % slide_obj
                #        print "actividadFlujo= %s" % slide_obj
                #        plantilla_flujo.actividades.remove(actividadFlujo)

                    plantilla_flujo.actividades.add(actividadFlujo)
                    plantilla_flujo.save()

                for actividad in plantilla_flujo.actividades.all():
                    print "actividad %s" % actividad
                    print "actividad.pk %s - slides %s" % (actividad.pk, slides)
                    afp = ActividadFlujoPlantilla.objects.get(pk=actividad.pk)
                    actividad_flujo = ActividadFlujo.objects.get(nombre=afp.nombre)
                    print "afp %s - %s" % (afp.pk, afp)
                    print "actividad_flujo %s-> %s - slides %s" % (actividad_flujo, actividad_flujo.pk, slides)
                    if actividad not in lista_flujo_act:
                        print "se remueve %s" % afp
                        plantilla_flujo.actividades.remove(actividad)

                print "plantilla %s" % plantilla_flujo
                return error



        if 'inactive' in request.POST:
            inactive_list = request.POST.getlist('actividad[]')
            print 'inactive_list: %s :' % inactive_list
            print "request %s" % request.POST
            resultado = update_slides(inactive_list, active=False)
            print "Resultado= %s" % resultado
            if resultado:
                mensaje_error_repetido = 'Ya existe una plantilla de flujo ese nombre, escriba otro nombre.'
                print "mensaje= %s" % mensaje_error_repetido
                return render(request, 'flujos/create_ajax.html', locals())

        print "en views %s" % lista_flujo_act
        # form = PlantillaFlujoCreateForm(request.POST, lista=lista_flujo_act)

        # if form.is_valid():
            #for act in inactive:

        #    form.save()

        #    return HttpResponseRedirect(reverse('flujos:index'))



    #else:

        # form = PlantillaFlujoCreateForm()


    return render(request, 'flujos/update_ajax.html', locals())



class ActividadCreate(CreateView):
    """
    Clase que despliega el formulario para la creacion de actividades.

    @ivar form_class: Formulario que se utiliza para la creacion de actividades
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = ActividadCreateForm
    template_name = 'flujos/create_actividad.html'

    def form_valid(self, form):
        return super(ActividadCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('flujos:create')


class FlujosProyectoIndex(generic.ListView):
    template_name = 'flujos/flujos_proyecto_index.html'
    context_object_name = 'flujo_list'

    def get_queryset(self):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['pk_proyecto'])
        #print Flujo.objects.filter(proyecto=self.proyecto).order_by('pk')

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

        return Flujo.objects.filter(proyecto=self.proyecto).order_by('pk')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(FlujosProyectoIndex, self).get_context_data(**kwargs)
        # Add in the publisher
        context['proyecto'] = self.proyecto
        context['roles_de_proyecto'] = self.roles_de_proyecto
        context['permisos'] = self.todos_permisos

        return context


class FlujoProyectoAsignar(UpdateView):
    form_class = AsignarFlujoProyectoForm
    template_name = 'flujos/asignar.html'
    context_object_name = 'proyecto'

    def get_object(self, queryset=None):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return obj

    def get_success_url(self):
        obj = Proyecto.objects.get(pk=self.kwargs['pk_proyecto'])
        return reverse('flujos:flujos_proyecto_index', args=[obj.pk])

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(FlujoProyectoAsignar, self).get_form_kwargs()
        # Update the kwargs with the user_id
        kwargs['user'] = self.request.user
        return kwargs