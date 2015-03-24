from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gpsk.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'gpsk.views.home', name='home'),
    url(r'^login/$', 'gpsk.views.custom_login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/login/'}, name='logout'),

)
