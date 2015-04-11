from django.views import generic
from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse

from forms import FlujoCreateForm, ActividadCreateForm
from models import Flujo


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

