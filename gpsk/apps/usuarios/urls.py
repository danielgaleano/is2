from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.UserIndexView.as_view()), name='index'),
                       url(r'^create/$', login_required(views.UserCreate.as_view()), name='create'),
                       url(r'^update/(?P<pk>\d+)/$', login_required(views.UserUpdate.as_view()), name='update'),
                       url(r'^delete/(?P<pk_usuario>\d+)/$', 'usuarios.views.inactivar_usuario', name='delete'),
                       url(r'^activate/(?P<pk_usuario>\d+)/$', 'usuarios.views.activar_usuario', name='activate'),
                       )