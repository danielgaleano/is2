from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = patterns('apps',
                       url(r'^$', login_required(views.UserIndexView.as_view()), name='index'),
                       url(r'^create/$', login_required(views.UserCreate.as_view()), name='create'),
                       url(r'^update/(?P<pk>\d+)/$', login_required(views.UserUpdate.as_view()), name='update'),
                       url(r'^delete/(?P<pk_usuario>\d+)/$', 'usuarios.views.inactivar_usuario', name='delete'),
                       url(r'^activate/(?P<pk_usuario>\d+)/$', 'usuarios.views.activar_usuario', name='activate'),
                       url(r'^(?P<pk>\d+)/roles/asignar/$', login_required(views.UserRoles.as_view()),
                           name='user_roles'),
                       url(r'^update/(?P<pk_usuario>\d+)/change_password/$', 'usuarios.views.user_change_password',
                           name='change_password'),
                       url(r'^(?P<pk>\d+)/roles/$', login_required(views.DetailViewRoles.as_view()),
                           name='detail_roles'),
                       )