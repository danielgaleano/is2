from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.IndexView.as_view()), name='index'),
                       # url(r'^create/$', login_required(views.FlujoCreate.as_view()), name='create'),
                       url(r'^create/actividad/$', login_required(views.ActividadCreate.as_view()),
                           name='create_actividad'),
                       #url(r'^create/$', login_required(views.FlujoCreate.as_view()), name='create'),
                       url(r'^create/$', 'flujos.views.crear_plantilla_flujo', name='create'),
                       #url(r'^create/$', 'flujos.views.prueba', name='create'),
                       url(r'^update/(?P<pk_plantilla_flujo>\d+)/$', 'flujos.views.editar_plantilla_flujo', name='update'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/$', login_required(views.FlujosProyectoIndex.as_view()),
                           name='flujos_proyecto_index'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/asignar/$', login_required(views.FlujoProyectoAsignar.as_view()),
                           name='asignar'),
                       )