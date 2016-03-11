// highchart global options
$(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
    });

// get local datetime ISO string
function getISOString(minute){
    minute = typeof minute !== 'undefined' ? minute : 0;
    var current = new Date();
    var timezoneOffset = current.getTimezoneOffset() * 60 * 1000;
    var localDate = new Date(current.getTime() - timezoneOffset);
    localDate.setMinutes(localDate.getMinutes() - minute);
    return localDate.toISOString().replace('Z', '').slice(0, 16);
}

// update chart
function chart_update(chart, url, from, to, auto, btn_ctrl){
    if (!auto){
        $('#chart-container').fadeTo(1000, 0.2);
        if (btn_ctrl){
            $('#chart_show_btn').attr('disabled', true)
        }
    }
    $.ajax({
        url: url,
        type: 'GET',
        dataType: "json",
        data: {'from': from, 'to': to, 'auto_update': auto},
        success: function(reply) {
            if (auto) {
                reply.forEach(function(item, i, arr){
                    if (typeof (chart.series[i]) !== 'undefined') {
                        chart.series[i].addPoint(reply[i].data, true, true);
                    }
                })
            }
            else {
                while(chart.series.length > 0){
                    chart.series[0].remove();
                }
                reply.forEach(function(item, i, arr){
                    chart.addSeries(reply[i], false)
                });
                chart.redraw();

                if (!auto){
                    if (btn_ctrl){
                        $('#chart_show_btn').attr('disabled', false);
                    }
                    $('#chart-container').fadeTo(2000, 1);
                }
            }
        },
        error: function(xhr,status,error){
            //alert('Не удалось получить данные с сервера');
            $('#chart-container').fadeTo(1000, 1);
            if (btn_ctrl){
                $('#chart_show_btn').attr('disabled', false);
            }
        }
    });

}

$(document).ready(function(){
    var current_url = window.location.pathname,
        chart_url = current_url.replace('graphic', 'update'),
        color_url = current_url.replace('graphic', 'edit'),
        $input_from = $('#from'),
        $input_to = $('#to'),
        $btn_chart_show = $('#chart_show_btn'),
        chart = new Highcharts.Chart({
        chart: {
            renderTo: 'chart-container',
            zoomType: 'xy',
            //backgroundColor: 'transparent',
            //borderColor: '#ffff7f',
            //borderWidth: 2,
            //borderRadius: 20,
        },
        credits: {
            enabled: false
        },
        title: {
            text: ''
        },
        xAxis: {
            type: 'datetime',
            lineColor: 'black',
            tickColor: 'black',
            tickWidth: 2,
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%e. %b %H:%M',
                day: '%e. %b',
                month: '%b \'%y',
                year: '%Y'
            }
        },
        yAxis: {
            //gridLineColor: '#be7dff'
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
    function auto_update(){
        var id = setInterval(function(){
            var from = getISOString(60),
                to = getISOString();
            $input_from.val(from);
            $input_to.val(to);
            chart_update(chart, chart_url, from, to, chart.series.length > 0, false)
        }, 3000);
        return id;
    }
    var id = auto_update();

    $("#chart_type").change(function(){
        if ($(this).val() == 'online'){
             while(chart.series.length > 0){
                    chart.series[0].remove();
                }
            $input_from.attr('disabled', true);
            $input_to.attr('disabled', true);
            $btn_chart_show.attr({'disabled': true, style:'color: #5d5d5d'});
            id = auto_update();
        }
        else{
            clearInterval(id);
            $input_from.attr('disabled', false);
            $input_to.attr('disabled', false);
            $btn_chart_show.attr({'disabled': false, style:'color: black'});
        }
    });

    $('.color').change(function(){
        var color = $(this).val(),
            name = $(this).attr('name'),
            id = $(this).attr('id');
        var chart_number = parseInt(id) - 1;
        //alert(chart_number);
        chart.series[chart_number].options.color = color;
        chart.series[chart_number].update(chart.series[chart_number].options);
        $.ajax({
                url: color_url,
                type: 'GET',
                data: {
                    'name': name,
                    'color': color
                },
                success: function(){
                }
        });
    });

    $btn_chart_show.click(function(){
       chart_update(chart, chart_url,  $input_from.val(), $input_to.val(), false, true);
    });

});

