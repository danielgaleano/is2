from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.IndexView.as_view()), name='index'),
                       url(r'^create/$', login_required(views.RolCreate.as_view()), name='create'),
                       url(r'^update/(?P<pk>\d+)/$', login_required(views.RolUpdate.as_view()), name='update'),
                       url(r'^delete/(?P<pk_rol>\d+)/$', 'roles.views.eliminar_rol', name='delete'),
                       url(r'^(?P<pk>\d+)/permisos/$', login_required(views.RolPermisos.as_view()),
                           name='rol_permisos')
                       )
