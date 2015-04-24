from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('apps',
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/$', login_required(views.IndexView.as_view()), name='index'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/create/$', login_required(views.UserStoryCreate.as_view()), name='create'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/update/(?P<pk_user_story>\d+)/$', login_required(views.UserStoryUpdatePO.as_view()), name='update'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/update_sm/(?P<pk_user_story_sm>\d+)/$', login_required(views.UserStoryUpdateSM.as_view()), name='update_sm'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/delete/(?P<pk_user_story>\d+)/$', 'user_stories.views.descartar_user_story', name='delete'),
                       url(r'^proyecto/(?P<pk_proyecto>\d+)/historial/(?P<pk_user_story>\d+)/$', login_required(views.VerHistorialUserStory.as_view()), name='historial'),
                       #url(r'^(?P<pk>\d+)/$', 'proyectos.views.proyecto_index', name='proyecto_index'),
                       #url(r'^(?P<pk_proyecto>\d+)/equipo/add/$', login_required(views.AddMiembro.as_view()),
                       #    name='add_miembro'),
                       #url(r'^(?P<pk_proyecto>\d+)/equipo/$', 'proyectos.views.listar_equipo', name='equipo_list'),
                       #url(r'^(?P<pk_proyecto>\d+)/equipo/delete/(?P<pk_user>\d+)/$', 'proyectos.views.delete_miembro',
                       #    name='delete_miembro'),
                       #url(r'^(?P<pk_proyecto>\d+)/equipo/rol/(?P<pk_user>\d+)/$',
                       #    login_required(views.RolMiembro.as_view()), name='rol_miembro'),
                       )