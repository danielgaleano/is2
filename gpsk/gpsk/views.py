from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse



@login_required(login_url='/login/')
def home(request):
    template = 'index.html'
    return render(request, template, locals())


def custom_login(request):
    template = 'index.html'
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    else:
        return login(request, template_name='login.html')
