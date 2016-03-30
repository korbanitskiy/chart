$(document).ready(function(){
    // highchart global options
    $(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
    });
    // graphic control object
    var graphic = {
    object: null,                           // highcharts object
    duration: 120,                          // graphic duration in minutes
    update_interval: 5000,                  // interval for auto update in milliseconds
    id: null,                               // id for setInterval
    from: null,
    to: null,
    clearData: function(){
        while(graphic.object.series.length > 0){
            graphic.object.series[0].remove();
        }
    },
    timeWrite: function(){
        var current = new Date(),
            timezoneOffset = current.getTimezoneOffset() * 60 * 1000,
            to = new Date(current.getTime() - timezoneOffset),
            from = to.setMinutes(to.getMinutes() - graphic.duration);
        graphic.to = to.toISOString().replace('Z', '').slice(0, 16);
        graphic.from = from.toISOString().replace('Z', '').slice(0, 16);
        $('#to').val(graphic.to);
        $('#from').val(graphic.from);
    },
    timeRead: function(){
        graphic.from = $('#from').val();
        graphic.to = $('#to').val();
    },
    updateAllPoints: function(url){
        graphic.object.showLoading();
        $('#chart_show_btn').attr('disabled', true);
        $.ajax({
            url: url,
            type: 'GET',
            dataType: "json",
            data: {'from': graphic.from, 'to': graphic.to, 'auto_update': false},
            success: function(reply){
                reply.forEach(function(item, i){
                    graphic.object.addSeries(item, false);
                    graphic.object.series[i].options.step = 'left';
                });
                graphic.object.redraw();
                graphic.object.hideLoading();
                $('#chart_show_btn').attr('disabled', false);
            }
        });
    },
    updateLastPoint: function(url){
        $.ajax({
            url: url,
            type: 'GET',
            dataType: "json",
            data: {'from': graphic.from, 'to': graphic.to, 'auto_update': true},
            success: function (reply) {
                graphic.object.series.forEach(function (item, i) {
                    var oldPointRightTime = item.data.slice(-1)[0].x,
                        oldPointLeftTime = item.data[0].x,
                        newPointTime = reply[i].data[0];
                    if (oldPointRightTime >= newPointTime) {
                        reply[i].data[0] = new Date().getTime();
                    }
                    var need_shift = (reply[i].data[0] - oldPointLeftTime) > graphic.duration * 60 * 1000; //difference in milliseconds
                    item.addPoint(reply[i].data, true, need_shift);
                });
            }
        });
    },
    startAutoUpdate: function(url){
        if (id == null){
            graphic.id = setInterval(function(){
                graphic.timeWrite();
                graphic.updateLastPoint(url);
            }, graphic.update_interval);
        }
    },
    stopAutoUpdate: function(){
        if (graphic.id != null){
            clearInterval(graphic.id);
            graphic.id = null;
        }
    }
};

    var current_url = window.location.pathname,
        chart_url = current_url.replace('graphic', 'update'),
        color_url = current_url.replace('graphic', 'edit');
        graphic.object = new Highcharts.Chart({
        chart: {
            renderTo: 'chart-container',
            zoomType: 'xy'
        },
        title: null,
        credits: {
            enabled: false
        },
        xAxis: {
            type: 'datetime',
            lineColor: 'black',
            tickColor: 'black',
            tickWidth: 2,
            dateTimeLabelFormats: {
                minute: '%e. %b %H:%M',
                hour: '%e. %b %H:%M',
                day: '%e. %b',
                month: '%b \'%y',
                year: '%Y'
            }
        },
        tooltip: {
            valueDecimals: 3
        },
        yAxis: {
            labels: {
                style: {
                    color: '#00',
                    font: '12px Verdana, sans-serif'
                }
            }
        },
        legend: {
            backgroundColor: '#eeeeee'
        }
    });
    graphic.timeWrite();
    graphic.updateAllPoints();
    graphic.startAutoUpdate(chart_url);

    $("#chart_type").change(function(){
        if ($(this).val() != 'online'){
            graphic.stopAutoUpdate();
            $('#from').attr('disabled', false);
            $('#to').attr('disabled', false);
            $('#chart_show_btn').attr({'disabled': false, style:'color: black'});

        }
        else{
            graphic.clearData();
            graphic.timeWrite();
            graphic.updateAllPoints(chart_url);
            graphic.startAutoUpdate(chart_url);
        }
    });

    $('.color').change(function(){
        var color = $(this).val(),
            name = $(this).attr('name'),
            num = parseInt($(this).attr('id')) - 1;
        $.ajax({
                url: color_url,
                type: 'GET',
                data: {'name': name, 'color': color},
                success: function(){
                     chart.series[num].options.color = color;
                     chart.series[num].update(chart.series[num].options);
                }
        });
    });

     $('#chart_show_btn').click(function(){
         graphic.timeRead();
         graphic.updateAllPoints(chart_url)

    });
});
