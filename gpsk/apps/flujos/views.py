from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.proyectos.models import Proyecto
from forms import PlantillaFlujoCreateForm, ActividadCreateForm, AsignarFlujoProyectoForm, FlujoCreateForm
from models import Flujo, Actividad, ActividadFlujo, Estado


class IndexView(generic.ListView):
    """
    Clase que despliega la lista completa de flujos en el Index
    de la aplicacion Proyecto.

    @ivar queryset: Consulta a la base de datos
    @type queryset: django.db.models.query

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Flujo
    template_name = 'flujos/index.html'


class FlujoCreate(CreateView):
    form_class = FlujoCreateForm
    template_name = 'flujos/create.html'

    def form_valid(self, form):
        return super(FlujoCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse( 'flujos:index')



class PlantillaFlujoCreate(CreateView):
    """
    Clase que despliega el formulario para la creacion de flujos.

    @ivar form_class: Formulario que se utiliza para la creacion de flujos
    @type form_class: django.forms

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    form_class = PlantillaFlujoCreateForm
    template_name = 'flujos/create.html'

    def form_valid(self, form):
        return super(PlantillaFlujoCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('flujos:index')

@csrf_exempt
def crear_plantilla_flujo(request):
    slide_list = Actividad.objects.all()
    active = []
    inactive = []

    lista_flujo_act = []

    for slide in slide_list:
        active.append(slide)
    if request.method == 'POST':
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
            print id_list
            clean_ids = clean_id_list(id_list)
            print clean_ids
            #slides = Actividad.objects.filter(pk__in=clean_ids)
            slides = clean_ids
            print slides

            #lista_flujo_act = []

            for ele in slides:
                act = Actividad.objects.get(pk=int(ele))
                nueva_actividad_flujo = ActividadFlujo.objects.create(nombre=act.nombre, orden=act.orden)

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
                actividadFlujo = ActividadFlujo.objects.get(pk=slide_obj.pk)

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

        if 'inactive' in request.POST:
            inactive_list = request.POST.getlist('actividad[]')
            print 'inactive_list: %s :' % inactive_list
            print "request %s" % request.POST
            update_slides(inactive_list, active=False)

        print "en views %s" % lista_flujo_act
        form = PlantillaFlujoCreateForm(request.POST, lista=lista_flujo_act)

        if form.is_valid():
            #for act in inactive:

            form.save()



            return HttpResponseRedirect(reverse('flujos:index'))

    else:
        form = PlantillaFlujoCreateForm()

    return render(request, 'flujos/create.html', locals())


@csrf_exempt
def editar_plantilla_flujo(request):
    slide_list = Actividad.objects.all()
    active = []
    inactive = []

    for slide in slide_list:
        active.append(slide)
    if request.method == 'POST':
        print("POST")
        form = FlujoUpdateForm(request.POST)

        def clean_id_list(id_list):
            clean_id_list = []
            for item in id_list:
                try:
                    clean_id_list.append(int(item))
                except ValueError:
                    pass
            return clean_id_list

        def update_slides(id_list, active, trash=False):
            print id_list
            clean_ids = clean_id_list(id_list)
            print clean_ids
            #slides = Actividad.objects.filter(pk__in=clean_ids)
            slides = clean_ids
            print slides

            lista_flujo_act = []

            for ele in slides:
                act = Actividad.objects.get(pk=int(ele))
                nueva_actividad_flujo = ActividadFlujo.objects.create(nombre=act.nombre, orden=act.orden)

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
                actividadFlujo = ActividadFlujo.objects.get(pk=slide_obj.pk)

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

        #if 'active' in request.POST:
        #    active_list = request.POST.getlist('actividad[]')
        #    update_slides(active_list, active=True)

        if 'inactive' in request.POST:
            inactive_list = request.POST.getlist('actividad[]')
            print 'inactive_list: %s :' % inactive_list
            print "request %s" % request.POST
            update_slides(inactive_list, active=False)

        if form.is_valid():
            #for act in inactive:


            form.save()


            return HttpResponseRedirect(reverse('flujos:index'))

    else:
        form = FlujoUpdateForm()

    return render(request, 'flujos/create.html', locals())



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
        return Flujo.objects.filter(proyecto=self.proyecto).order_by('pk')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(FlujosProyectoIndex, self).get_context_data(**kwargs)
        # Add in the publisher
        context['proyecto'] = self.proyecto

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