# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, UpdateView, View, ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
import datetime
import json
import models
import calendar
# import time
# from django.db import connection


class Index(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['zone'] = 'Index'
        return context


class Login(View):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
            return render(request, 'index.html', {'zone': 'Index'})
        else:
            return render(request, 'login.html', {'zone': 'Login'})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'index.html', {'zone': 'Index'})
        else:
            return render(request, 'login.html', {'message': 'This user can not be found', 'zone': 'Login'})


class Graphic(DetailView):
    template_name = 'graphic.html'

    def get_context_data(self, **kwargs):
        context = super(Graphic, self).get_context_data(**kwargs)
        context['cur_trend_num'] = int(self.kwargs['trend'])
        context['trend_qs'] = self.queryset
        context['zone'] = self.kwargs['zone']
        sensors = []
        for i in range(1, 9):
            sensor = getattr(self.object, 'trend' + str(i))
            if sensor:
                trend = {'number': i,
                         'name': sensor.name,
                         'description': sensor.description,
                         'color': getattr(self.object, 'color' + str(i))}
                sensors.append(trend)
        context['sensors'] = sensors
        return context

    def get_object(self, queryset=None):
        self.queryset = models.Trend.objects.filter(location__name=self.kwargs['zone'])
        try:
            obj = self.queryset.get(number=self.kwargs['trend'])
        except KeyError:
            obj = None
        return obj


class TrendEdit(UpdateView):
    template_name = 'trend_edit.html'
    fields = ['trend' + str(i) for i in range(1, 9)]

    def get_object(self, queryset=None):
        queryset = models.Trend.objects.filter(location__name=self.kwargs['zone'])
        obj = queryset.get(number=self.kwargs['trend'])
        return obj

    def get_success_url(self):
        trend = (self.kwargs['trend'])
        zone = (self.kwargs['zone'])
        return reverse('graphic', args=[zone, trend])

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            obj = self.get_object()
            color_name = request.GET['name']
            obj.__dict__[color_name] = request.GET['color']
            obj.save()
            return HttpResponse(status=200)
        return super(TrendEdit, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrendEdit, self).get_context_data(**kwargs)
        for field_name in self.fields:
            context['form'].fields[field_name].queryset = models.Sensor.objects.filter(location__name=self.kwargs['zone'])
        return context


class Message(ListView):
    template_name = 'message.html'

    def get_queryset(self):
        try:
            self.date_to = datetime.datetime.strptime(self.request.GET['to'], '%Y-%m-%dT%H:%M')
            self.date_from = datetime.datetime.strptime(self.request.GET['from'], '%Y-%m-%dT%H:%M')
        except KeyError:
            self.date_to = datetime.datetime.now()
            self.date_from = self.date_to - datetime.timedelta(days=1)

        self.message_type = self.request.GET.get('type', 'All')
        self.message_state = self.request.GET.get('state', 'All')

        qs = models.MessageList.objects.filter(message__location__name=self.kwargs['zone'])\
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
        context['types'] = models.MessageType.objects.all()
        context['cur_type'] = self.message_type
        context['states'] = ('Active', 'Non Active')
        context['cur_state'] = self.message_state
        return context


class Mechanism(ListView):
    template_name = 'mechanism.html'

    def get_queryset(self):
        try:
            self.date_to = datetime.datetime.strptime(self.request.GET['to'], '%Y-%m-%dT%H:%M')
            self.date_from = datetime.datetime.strptime(self.request.GET['from'], '%Y-%m-%dT%H:%M')
        except KeyError:
            self.date_to = datetime.datetime.now()
            self.date_from = self.date_to - datetime.timedelta(days=1)

        self.location = 'Pasteurizer' + self.kwargs['pasteurizer']

        qs = models.StateList.objects.filter(mechanism__location__name=self.location)\
                                     .filter(time_stamp__range=(self.date_from, self.date_to))\
                                     .order_by('-time_stamp')

        self.name = self.request.GET.get('mechanism', 'All')
        if self.name != 'All':
            qs = qs.filter(mechanism__name=self.name)
        return qs

    def get_context_data(self, **kwargs):
        context = super(Mechanism, self).get_context_data(**kwargs)
        context['date_to'] = self.date_to.strftime('%Y-%m-%dT%H:%M')
        context['date_from'] = self.date_from.strftime('%Y-%m-%dT%H:%M')
        context['mechanisms'] = models.Mechanism.objects.filter(location__name=self.location)
        context['cur_mech'] = self.name
        context['pasteurizer'] = self.kwargs['pasteurizer']
        return context


def chart_update(request, zone, trend):
    try:
        date_to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%dT%H:%M')
        date_from = datetime.datetime.strptime(request.GET['from'], '%Y-%m-%dT%H:%M')
        auto_update = json.loads(request.GET['auto_update'])
    except KeyError:
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=1)
        auto_update = False
    trend_qs = models.Trend.objects.get(location__name=zone, number=trend)
    sensors = []
    for x in range(1, 9):
        attr_name = 'trend' + str(x)
        trend = getattr(trend_qs, attr_name)
        if trend is not None:
            obj = {'name': trend.description,
                   'color': getattr(trend_qs, attr_name.replace('trend', 'color')),
                   'data': [],
                   'tooltip': {'valueSuffix': ' ' + trend.egu}
                   }
            if auto_update:
                values_qs = models.Value.objects.filter(sensor__id=trend.id).order_by('-id')[0]
                time_change = calendar.timegm(values_qs.change.timetuple()) * 1000
                obj['data'] = [time_change, values_qs.value]
            else:
                values_qs = models.Value.objects.filter(sensor__id=trend.id, change__range=(date_from, date_to))
                for i in values_qs:
                    # time_change = time.mktime(x.change.utctimetuple()) * 1000
                    time_change = calendar.timegm(i.change.timetuple()) * 1000
                    obj['data'].append([time_change, i.value])
            sensors.append(obj)
    return HttpResponse(json.dumps(sensors))

