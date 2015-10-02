from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', 'gpsk.views.home', name='home'),

                       url(r'^login/$', 'gpsk.views.custom_login', name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}, name='logout'),

                       url(r'^reset/$', 'gpsk.views.reset', name='reset'),
                       url(r'^reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           'gpsk.views.reset_confirm', name='reset_confirm'),
                       url(r'^reset/done/$', 'gpsk.views.reset_done', name='reset_done'),
                       url(r'^reset/complete/$', 'gpsk.views.reset_complete', name='reset_complete'),

                       url(r'^perfil/$', 'gpsk.views.user_profile', name='user_profile'),
                       url(r'^perfil/password_change/$', 'gpsk.views.perfil_change_password',
                           name='profile_password_change'),

                       url(r'^usuarios/', include('apps.usuarios.urls', namespace="usuarios")),
                       url(r'^clientes/', include('apps.clientes.urls', namespace="clientes")),
                       url(r'^roles/', include('apps.roles.urls', namespace="roles")),
                       url(r'^roles_proyecto/', include('apps.roles_proyecto.urls', namespace="roles_proyecto")),
                       url(r'^proyectos/', include('apps.proyectos.urls', namespace="proyectos")),
                       url(r'^flujos/', include('apps.flujos.urls', namespace="flujos")),
                       url(r'^user_stories/', include('apps.user_stories.urls', namespace="user_stories")),
                       url(r'^sprints/', include('apps.sprints.urls', namespace="sprints")),
                       url(r'^files/', include('db_file_storage.urls')),
                       )+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
