from django.conf.urls import patterns, include, url
from trend import views
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^$', views.Index.as_view(), name='index'),
        url(r'^login/$', views.Login.as_view(), name='login'),
        url(r'^pasteurizer/(?P<pasteurizer>[0-9]+)/(?P<trend>[0-9]+)/$', views.Pasteurizer.as_view(), name='pasteurizer'),
        url(r'^edit/(?P<pasteurizer>[0-9]+)/(?P<trend>[0-9]+)/$', views.TrendEdit.as_view(), name='trend_edit'),
        url(r'^update/(?P<pasteurizer>[0-9]+)/(?P<trend>[0-9]+)/$', views.ajax_update),
        url(r'^message/(?P<pasteurizer>[0-9]+)/$', views.Message.as_view(), name='message'),
        url(r'^mechanism/(?P<pasteurizer>[0-9]+)/$', views.Mechanism.as_view(), name='mechanism'),
        )


