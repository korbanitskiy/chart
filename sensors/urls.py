from django.conf.urls import patterns, url
from views import Graphic, TrendEdit, Explosion, online_update


urlpatterns = patterns('',
                       url(r'^graphic/(?P<location>\w+)/(?P<trend>[0-9]+)/$', Graphic.as_view(), name='graphic'),
                       url(r'^edit/(?P<location>\w+)/(?P<trend>[0-9]+)/$', TrendEdit.as_view(), name='edit'),
                       url(r'^update/(?P<location>\w+)/(?P<trend>[0-9]+)/$', online_update),
                       url(r'^explosion/(?P<location>\w+)/$', Explosion.as_view(), name='explosion'),
                       )
