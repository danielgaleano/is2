from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.IndexView.as_view()), name='index'),
                       # url(r'^create/$', login_required(views.FlujoCreate.as_view()), name='create'),
                       url(r'^create/actividad/$', login_required(views.ActividadCreate.as_view()),
                           name='create_actividad'),
                       url(r'^create/$', 'flujos.views.crear_flujo', name='create'),
                       )