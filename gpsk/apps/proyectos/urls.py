from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.IndexView.as_view()), name='index'),
                       url(r'^create/$', login_required(views.ProyectoCreate.as_view()), name='create'),
                       url(r'^update/(?P<pk>\d+)/$', login_required(views.ProyectoUpdate.as_view()), name='update'),
                       url(r'^ver/(?P<pk>\d+)/$', login_required(views.ProyectoVer.as_view()), name='ver'),
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
                       url(r'^(?P<pk>\d+)/reporte_grafico_sprints/$', 'proyectos.views.reporte_grafico_reportlab', name='reporte_grafico_sprints'),
                       url(r'^(?P<pk>\d+)/reporte_grafico_sprints_download/$', 'proyectos.views.reporte_grafico_reportlab_download', name='reporte_grafico_sprints_download'),
                       url(r'^(?P<pk>\d+)/reporte_trabajo_usuario/$', 'proyectos.views.proyecto_reporte_trabajos_usuario', name='reporte_trabajo_usuario'),
                       url(r'^(?P<pk>\d+)/reporte_trabajo_usuario_download/$', 'proyectos.views.proyecto_reporte_trabajos_usuario_download', name='reporte_trabajo_usuario_download'),
                       url(r'^(?P<pk>\d+)/reporte_actividades/$', 'proyectos.views.proyecto_reporte_actividades', name='proyecto_reporte_actividades'),
                       url(r'^(?P<pk>\d+)/reporte_actividades_download/$', 'proyectos.views.proyecto_reporte_actividades_download', name='proyecto_reporte_actividades_download'),
                       url(r'^(?P<pk>\d+)/reporte_product_backlog/$', 'proyectos.views.proyecto_reporte_product_backlog', name='proyecto_reporte_product_backlog'),
                       url(r'^(?P<pk>\d+)/reporte_product_backlog_download/$', 'proyectos.views.proyecto_reporte_product_backlog_download', name='proyecto_reporte_product_backlog_download'),
                       url(r'^(?P<pk>\d+)/reporte_sprint_backlog/$', 'proyectos.views.proyecto_reporte_sprint_backlog', name='proyecto_reporte_sprint_backlog'),
                       url(r'^(?P<pk>\d+)/reporte_sprint_backlog_download/$', 'proyectos.views.proyecto_reporte_sprint_backlog_download', name='proyecto_reporte_sprint_backlog_download'),
                       )
