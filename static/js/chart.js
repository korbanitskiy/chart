var graphic = {
    object: null,                           // highcharts object
    duration: 120,                          // graphic duration in minutes
    update_interval: 5000,                  // interval for auto update in milliseconds
    id: null,                               // id for setInterval


};


// highchart global options
$(function () {
        Highcharts.setOptions({
            global: {
                useUTC: false
            }
        });
    });
