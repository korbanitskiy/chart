from django.views.generic import ListView
import datetime
from models import MessageList, MessageType


class Message(ListView):
    template_name = 'message.html'

    def get_queryset(self):
        try:
            self.date_to = datetime.datetime.strptime(self.request.GET['to'], '%Y-%m-%dT%H:%M')
            self.date_from = datetime.datetime.strptime(self.request.GET['from'], '%Y-%m-%dT%H:%M')
        except KeyError:
            self.date_to = datetime.datetime.now()
            self.date_from = self.date_to - datetime.timedelta(hours=2)
        self.message_type = self.request.GET.get('type', 'All')
        self.message_state = self.request.GET.get('state', 'All')
        qs = MessageList.objects.filter(message__location__name=self.kwargs['location'])\
                                       .filter(time_stamp__range=(self.date_from, self.date_to))\
                                       .order_by('-time_stamp')
        if self.message_type != 'All':
            qs = qs.filter(message__type__text=self.message_type)
        if self.message_state != 'All':
            if self.message_state == 'Active':
                state = True
            else:
                state = False
            qs = qs.filter(state=state)
        return qs

    def get_context_data(self, **kwargs):
        context = super(Message, self).get_context_data(**kwargs)
        context['date_to'] = self.date_to.strftime('%Y-%m-%dT%H:%M')
        context['date_from'] = self.date_from.strftime('%Y-%m-%dT%H:%M')
        context['types'] = MessageType.objects.all()
        context['cur_type'] = self.message_type
        context['states'] = ('Active', 'Non Active')
        context['cur_state'] = self.message_state
        context['location'] = self.kwargs['location']
        return context
