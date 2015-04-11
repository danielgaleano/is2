from django.shortcuts import render
from models import Cliente
from django.views import generic
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView


class listarClientes(generic.ListView):
    model = Cliente
    template_name = 'clientes/index.html'


class crearCliente(CreateView):
    model = Cliente
    template_name = 'clientes/crear.html'

    def get_success_url(self):
        return reverse('clientes:index')


class actualizarCliente(UpdateView):
    model = Cliente
    template_name = 'clientes/actualizar.html'

    #def get_object(self, queryset=None):
     #   obj = Cliente.objects.get(pk = self.kwargs['pk'])
      #  return obj

    def get_success_url(self):
        return reverse('clientes:index')