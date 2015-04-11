from django.shortcuts import render
from models import Cliente
from django.views import generic
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView

class listarClientes(generic.ListView):
    """
    Clase que despliega la lista completa de clientes en el Index
    de la aplicacion Clientes

    @ivar model: Modelo que se utiliza para la creacion de clientes
    @type form_class: Cliente

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Cliente
    template_name = 'clientes/index.html'

class crearCliente(CreateView):
    """
    Clase que despliega el formulario para la creacion de clientes.

    @ivar model: Modelo que se utiliza para la creacion de clientes
    @type form_class: Cliente

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Cliente
    template_name = 'clientes/crear.html'
    
       

    def get_success_url(self):
        """
        Metodo que redirecciona al index de clientes una vez que los datos se hayan guardado correctamente.

        @type self: Cliente
        @param self: Informacion sobre la vista del cliente actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        return reverse('clientes:index')


class actualizarCliente(UpdateView):
    """
    Clase que despliega el formulario para la modficacion de clientes.

    @ivar model: Modelo que se utiliza para la creacion de clientes
    @type form_class: Cliente

    @ivar template_name: Nombre del template a utilizar en la vista
    @type template_name: string
    """
    model = Cliente
    template_name = 'clientes/actualizar.html'

    #def get_object(self, queryset=None):
     #   obj = Cliente.objects.get(pk = self.kwargs['pk'])
      #  return obj

    def get_success_url(self):
        """
        Metodo que redirecciona al index de clientes una vez que los datos se hayan guardado correctamente.

        @type self: Cliente
        @param self: Informacion sobre la vista del formulario actual

        @rtype: django.core.urlresolvers
        @return: redireccion al index de la aplicacion usuarios
        """
        return reverse('clientes:index')