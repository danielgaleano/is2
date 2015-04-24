from django.views import generic
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse
from django.shortcuts import render

from forms import FlujoCreateForm, ActividadCreateForm
from models import Flujo, Actividad

from django.views.decorators.csrf import csrf_exempt



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
        return reverse('flujos:index')

@csrf_exempt
def crear_flujo(request):
    slide_list = Actividad.objects.all()
    active = []
    inactive = []

    for slide in slide_list:
        active.append(slide)
    if request.method == 'POST':
        form = FlujoCreateForm(request.POST)

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
            slides = Actividad.objects.filter(pk__in=clean_ids)
            print slides
            sorting_counter = 1
            print "Hola"
            for slide in slides:
                print slide.orden
                if trash:
                    print "IF"
                    # While this is fine for my requirements, you may want
                    # to check permissions here (I have @login_required)
                    slide.delete()
                else:
                    print "Else"
                    slide.orden = sorting_counter
                    #slide.active = active
                    slide.save()
                    sorting_counter += 1

        #if 'active' in request.POST:
        #    active_list = request.POST.getlist('actividad[]')
        #    update_slides(active_list, active=True)

        if 'inactive' in request.POST:
            inactive_list = request.POST.getlist('actividad[]')
            update_slides(inactive_list, active=False)

        if form.is_valid():
            #for act in inactive:


            form.save()


    else:
        form = FlujoCreateForm()

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

