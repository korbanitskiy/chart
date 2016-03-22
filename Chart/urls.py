from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import Index, Login

admin.autodiscover()


urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^$', Index.as_view(), name='index'),
                       url(r'^login/$', Login.as_view(), name='login'),
                       url(r'^sensors/', include('sensors.urls', namespace='sensors')),
                       url(r'^messages/', include('messages.urls', namespace='messages')),



        )


