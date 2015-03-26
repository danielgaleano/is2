from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



@login_required(login_url='/login/')
def home(request):
    """
    Genera la vista home del sistema.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @rtype: django.http.HttpResponse
    @return: Renderiza index.html, la pagina de inicio del sistema
    """
    template = 'index.html'
    return render(request, template, locals())


def custom_login(request):
    """
    Genera la vista de login al sistema.

    @type request: django.http.HttpRequest
    @param request: Contiene informacion sobre la peticion actual

    @rtype: django.http.HttpResponseRedirect
    @return: Renderiza login.html si el usuario no esta autenticado o
            redirecciona a la vista home si el usuario esta autenticado.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request, template_name='login.html')
