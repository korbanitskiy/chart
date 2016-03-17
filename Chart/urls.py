from django.conf.urls import patterns, include, url
from trend import views
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^$', views.Index.as_view(), name='index'),
        url(r'^login/$', views.Login.as_view(), name='login'),
        url(r'^graphic/(?P<zone>\w+)/(?P<trend>[0-9]+)/$', views.Graphic.as_view(), name='graphic'),
        url(r'^edit/(?P<zone>\w+)/(?P<trend>[0-9]+)/$', views.TrendEdit.as_view(), name='trend_edit'),
        url(r'^update/(?P<zone>\w+)/(?P<trend>[0-9]+)/$', views.chart_update),
        url(r'^message/(?P<zone>\w+)/$', views.Message.as_view(), name='message'),
        url(r'^bottle/(?P<zone>\w+)/$', views.Bottle.as_view(), name='bottle'),

        # url(r'^mechanism/(?P<zone>[0-9]+)/$', views.Mechanism.as_view(), name='mechanism'),
        )


