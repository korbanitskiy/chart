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


class Login(View):

    def get(self, request):
        if request.user.is_authenticated():
            logout(request)
            return render(request, 'index.html')
        else:
            return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'index.html')
        else:
            return render(request, 'login.html', {'message': 'This user can not be found'})


class Pasteurizer(DetailView):
    template_name = 'pasteurizer.html'

    def get_context_data(self, **kwargs):
        context = super(Pasteurizer, self).get_context_data(**kwargs)
        context['trend'] = int(self.kwargs['trend'])
        context['trend_qs'] = self.queryset
        context['pasteurizer'] = self.kwargs['pasteurizer']

        trends = []
        for i in range(1, 9):
            sensor = getattr(self.object, 'trend' + str(i))
            if sensor:
                trend = {'name': sensor.name,
                         'description': sensor.description,
                         'color': getattr(self.object, 'color' + str(i))}
                trends.append(trend)
        context['trends'] = trends
        return context

    def get_object(self, queryset=None):
        self.queryset = models.Trend.objects.filter(location__name='Pasteurizer' + self.kwargs['pasteurizer'])
        try:
            obj = self.queryset.get(number=self.kwargs['trend'])
        except KeyError:
            obj = None
        return obj


class TrendEdit(UpdateView):
    template_name = 'trend_edit.html'
    fields = ['trend' + str(i) for i in range(1, 9)]

    def get_object(self, queryset=None):
        self.location = 'Pasteurizer' + self.kwargs['pasteurizer']
        queryset = models.Trend.objects.filter(location__name=self.location)
        obj = queryset.get(number=self.kwargs['trend'])
        return obj

    def get_success_url(self):
        trend = (self.kwargs['trend'])
        pasteurizer = (self.kwargs['pasteurizer'])
        return reverse('pasteurizer', args=[pasteurizer, trend])

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            obj = self.get_object()
            name = request.GET['name']
            obj.__dict__[name] = request.GET['color']
            obj.save()
            return HttpResponse(status=200)

        return super(TrendEdit, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrendEdit, self).get_context_data(**kwargs)
        for field_name in self.fields:
            context['form'].fields[field_name].queryset = models.Sensor.objects.filter(location__name=self.location)
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

        qs = models.MessageList.objects.filter(message__location__name='Pasteurizer' + self.kwargs['pasteurizer'])\
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
        context['pasteurizer'] = self.kwargs['pasteurizer']
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


def ajax_update(request, pasteurizer, trend):
    location = 'Pasteurizer' + pasteurizer
    trend_qs = models.Trend.objects.get(location__name=location, number=trend)
    try:
        date_to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%dT%H:%M')
        date_from = datetime.datetime.strptime(request.GET['from'], '%Y-%m-%dT%H:%M')
        auto_update = json.loads(request.GET['auto_update'])
    except KeyError:
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=1)
        auto_update = False

    sensors = []
    for name in ['trend' + str(x) for x in range(1, 9)]:
            trend = getattr(trend_qs, name)
            if trend is not None:
                obj = {'name': trend.name, 'color': getattr(trend_qs, name.replace('trend', 'color')), 'data': []}
                if auto_update:
                    values_qs = models.Value.objects.filter(sensor__id=trend.id).order_by('-id')[0]
                    time_change = calendar.timegm(values_qs.change.timetuple()) * 1000
                    obj['data'] = [time_change, values_qs.value]
                else:
                    values_qs = models.Value.objects.filter(sensor__id=trend.id, change__range=(date_from, date_to))
                    # print connection.queries
                    for x in values_qs:
                        # time_change = time.mktime(x.change.utctimetuple()) * 1000
                        time_change = calendar.timegm(x.change.timetuple()) * 1000
                        obj['data'].append([time_change, x.value])

                sensors.append(obj)
    return HttpResponse(json.dumps(sensors))

