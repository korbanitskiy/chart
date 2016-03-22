# -*- coding: UTF-8 -*-
from django.views.generic import DetailView, UpdateView, ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import datetime
import json
from models import Trend, Sensor, Value
import calendar


class Graphic(DetailView):
    template_name = 'graphic.html'

    def get_context_data(self, **kwargs):
        context = super(Graphic, self).get_context_data(**kwargs)
        context['cur_trend_num'] = int(self.kwargs['trend'])
        context['trend_qs'] = self.queryset
        context['location'] = self.kwargs['location']
        sensors = []
        for i in range(1, 9):
            sensor = getattr(self.object, 'trend' + str(i))
            if sensor:
                trend = {'number': i,
                         'name': sensor.name,
                         'description': sensor.description,
                         'color': getattr(self.object, 'color' + str(i)),
                         'egu': sensor.egu
                         }
                sensors.append(trend)
        context['sensors'] = sensors
        return context

    def get_object(self, queryset=None):
        self.queryset = Trend.objects.filter(location__name=self.kwargs['location'])
        obj = self.queryset.get(number=self.kwargs['trend'])
        return obj


class TrendEdit(UpdateView):
    template_name = 'trend_edit.html'
    fields = ['trend' + str(i) for i in range(1, 9)]

    def get_object(self, queryset=None):
        queryset = Trend.objects.filter(location__name=self.kwargs['location'])
        obj = queryset.get(number=self.kwargs['trend'])
        return obj

    def get_success_url(self):
        trend = (self.kwargs['trend'])
        location = (self.kwargs['location'])
        return reverse('sensors:graphic', args=[location, trend])

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
            context['form'].fields[field_name].queryset = Sensor.objects.filter(location__name=self.kwargs['location'])
        return context


class Explosion(ListView):
    template_name = 'explosion.html'

    def get_queryset(self):
        try:
            self.date_to = datetime.datetime.strptime(self.request.GET['to'], '%Y-%m-%dT%H:%M')
            self.date_from = datetime.datetime.strptime(self.request.GET['from'], '%Y-%m-%dT%H:%M')
        except KeyError:
            self.date_to = datetime.datetime.now()
            self.date_from = self.date_to - datetime.timedelta(hours=24)
        self.streamer = self.request.GET.get('streamer', 'All')
        object_list = []
        if self.streamer == 'All':
            qs = Sensor.objects.filter(location__name=self.kwargs['location'])
            for i in qs.values_list('id', flat=True):
                description = qs.get(id=i).description
                value = Value.objects.filter(sensor__id=i, change__range=(self.date_from, self.date_to)).count()
                if value > 0:
                    object_list.append({'name': description, 'value': value})
        else:
            explosions = Value.objects.filter(sensor__id=self.streamer, change__range=(self.date_from, self.date_to))\
                                      .order_by('-change')
            for explosion in explosions:
                options = {'explosion_number': explosion.value, 'explosion_date': explosion.change}
                for name in ('MonoActualSpeed', 'Pbeer_circul_Buf', 'Lbeer_circul_Buf', 'Vacum'):
                    qs = Value.objects.filter(sensor__name=name, change__lte=explosion.change).order_by('-change')
                    if qs.count() > 0:
                        options[name] = qs[0]
                    else:
                        options[name] = 'Нет данных'
                object_list.append(options)
        return object_list

    def get_context_data(self, **kwargs):
        context = super(Explosion, self).get_context_data(**kwargs)
        context['date_to'] = self.date_to.strftime('%Y-%m-%dT%H:%M')
        context['date_from'] = self.date_from.strftime('%Y-%m-%dT%H:%M')
        context['streamers'] = Sensor.objects.filter(location__name=self.kwargs['location'])
        context['location'] = self.kwargs['location']
        try:
            context['cur_streamer'] = int(self.streamer)
        except ValueError:
            context['cur_streamer'] = 'All'
        return context


def online_update(request, location, trend):
    try:
        date_to = datetime.datetime.strptime(request.GET['to'], '%Y-%m-%dT%H:%M')
        date_from = datetime.datetime.strptime(request.GET['from'], '%Y-%m-%dT%H:%M')
        auto_update = json.loads(request.GET['auto_update'])
    except KeyError:
        date_to = datetime.datetime.now()
        date_from = date_to - datetime.timedelta(hours=1)
        auto_update = False
    trend_obj = Trend.objects.get(location__name=location, number=trend)
    sensors = []
    for x in range(1, 9):
        attr_name = 'trend' + str(x)
        trend = getattr(trend_obj, attr_name)
        if trend is not None:
            obj = {'name': trend.description,
                   'color': getattr(trend_obj, attr_name.replace('trend', 'color')),
                   'data': [],
                   'tooltip': {'valueSuffix': ' ' + trend.egu}
                   }
            if auto_update:
                values_qs = Value.objects.filter(sensor__id=trend.id).order_by('-id')[0]
                time_change = calendar.timegm(values_qs.change.timetuple()) * 1000
                obj['data'] = [time_change, values_qs.value]
            else:
                values_qs = Value.objects.filter(sensor__id=trend.id, change__range=(date_from, date_to))
                for i in values_qs:
                    time_change = calendar.timegm(i.change.timetuple()) * 1000
                    obj['data'].append([time_change, i.value])
            sensors.append(obj)
    return HttpResponse(json.dumps(sensors))
