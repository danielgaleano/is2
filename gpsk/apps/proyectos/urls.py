from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.IndexView.as_view()), name='index'),
                       url(r'^create/$', login_required(views.ProyectoCreate.as_view()), name='create'),
                       url(r'^update/(?P<pk>\d+)/$', login_required(views.ProyectoUpdate.as_view()), name='update'),
                       url(r'^delete/(?P<pk_proyecto>\d+)/$', 'proyectos.views.eliminar_proyecto', name='delete'),
                       url(r'^(?P<pk>\d+)/$', 'proyectos.views.proyecto_index', name='proyecto_index'),
                       url(r'^iniciar/(?P<pk_proyecto>\d+)/$', 'proyectos.views.iniciar_proyecto', name='iniciar'),
                       url(r'^finalizar/(?P<pk_proyecto>\d+)/$', 'proyectos.views.finalizar_proyecto', name='finalizar'),
                       url(r'^(?P<pk_proyecto>\d+)/equipo/add/$', login_required(views.AddMiembro.as_view()),
                           name='add_miembro'),
                       url(r'^(?P<pk_proyecto>\d+)/equipo/$', 'proyectos.views.listar_equipo', name='equipo_list'),
                       url(r'^(?P<pk_proyecto>\d+)/equipo/delete/(?P<pk_user>\d+)/$', 'proyectos.views.delete_miembro',
                           name='delete_miembro'),
                       url(r'^(?P<pk_proyecto>\d+)/equipo/rol/(?P<pk_user>\d+)/$',
                           login_required(views.RolMiembro.as_view()), name='rol_miembro'),
                       url(r'^(?P<pk_proyecto>\d+)/equipo/horas/(?P<pk_user>\d+)/$',
                           login_required(views.HorasDeveloper.as_view()), name='horas_developer'),
                       url(r'^(?P<pk>\d+)/reportes/$', 'proyectos.views.proyecto_reportes', name='proyecto_reportes'),
                       url(r'^(?P<pk>\d+)/reporte_trabajo_equipo/$', 'proyectos.views.proyecto_reporte_trabajos_equipo', name='reporte_trabajo_equipo'),
                       url(r'^(?P<pk>\d+)/reporte_trabajo_equipo_download/$', 'proyectos.views.proyecto_reporte_trabajos_equipo_download', name='reporte_trabajo_equipo_download'),
                       )
