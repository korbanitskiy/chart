from django.conf.urls import patterns, url
from views import Message


urlpatterns = patterns('',
                       url(r'^(?P<location>\w+)/$', Message.as_view(), name='message'),
                       )
