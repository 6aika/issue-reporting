var opts = {
    lines: 11 // The number of lines to draw
    , length: 0 // The length of each line
    , width: 14 // The line thickness
    , radius: 33 // The radius of the inner circle
    , scale: 1 // Scales overall size of the spinner
    , corners: 1 // Corner roundness (0..1)
    , color: '#000' // #rgb or #rrggbb or array of colors
    , opacity: 0.25 // Opacity of the lines
    , rotate: 0 // The rotation offset
    , direction: 1 // 1: clockwise, -1: counterclockwise
    , speed: 1.2 // Rounds per second
    , trail: 60 // Afterglow percentage
    , fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
    , zIndex: 2e9 // The z-index (defaults to 2000000000)
    , className: 'spinner' // The CSS class to assign to the spinner
    , top: '50%' // Top position relative to parent
    , left: '50%' // Left position relative to parent
    , shadow: false // Whether to render a shadow
    , hwaccel: false // Whether to use hardware acceleration
    , position: 'absolute' // Element positioning
};

function humanize(value) {
    return Math.floor(value) + 'pv ' + Math.floor((value * 86400 % 86400) / 3600) + 'h';
};

var serviceStatisticsDiv = document.getElementById('serviceStatistics');
var agencyStatisticsDiv = document.getElementById('agencyStatistics');
var timeStatisticsDiv = document.getElementById('timeStatistics');

var serviceStatisticsSpinner = new Spinner(opts).spin(serviceStatisticsDiv);
var agencyStatisticsSpinner = new Spinner(opts).spin(agencyStatisticsDiv);
var timeStatisticsSpinner = new Spinner(opts).spin(timeStatisticsDiv);

$.getJSON("/api/v1/statistics/services/", function (data) {
    var services = ['x'];
    var total = ['kaikki'];
    var closed = ['suljetut'];
    var fixing_time = ['Korjausaika päivissä ja tunneissa'];
    $.each(data, function (key, item) {
        services.push(item.service_name);
        total.push(item.total);
        closed.push(item.closed);
        fixing_time.push(item.median_sec / 86400)
    });

    c3.generate({
        bindto: '#serviceStatistics',
        data: {
            x: 'x',
            columns: [
                services,
                total,
                closed
            ],
            type: 'bar'
        },
        axis: {
            y: {
                tick: {
                    format: d3.format("d")
                }
            },
            x: {
                type: 'category', // this needed to load string x value
                tick: {
                    rotate: 75,
                    multiline: false
                },
                height: 130
            }
        }
    });

    serviceStatisticsSpinner.stop();

    c3.generate({
        bindto: '#timeStatistics',
        data: {
            x: 'x',
            columns: [
                services,
                fixing_time
            ],
            type: 'bar'
        },
        axis: {
            y: {
                tick: {
                    format: d3.format("d")
                }
            },
            x: {
                type: 'category', // this needed to load string x value
                tick: {
                    rotate: 75,
                    multiline: false
                },
                height: 130
            }
        },
        tooltip: {
            format: {
                value: humanize
            }
        }
    });

    timeStatisticsSpinner.stop();
});
$.getJSON("/api/v1/statistics/agencies/", function (data) {
    var agencies = ['x'];
    var total = ['kaikki'];
    var closed = ['suljetut'];
    $.each(data, function (key, item) {
        if (key > 9) return;
        agencies.push(item.agency_responsible);
        total.push(item.total);
        closed.push(item.closed);
    });
    c3.generate({
        bindto: '#agencyStatistics',
        padding: {
            right: 12
        },
        data: {
            y: {
                tick: {
                    format: d3.format("d")
                }
            },
            x: 'x',
            columns: [
                agencies,
                total,
                closed
            ],
            type: 'bar'
        },
        zoom: {
            enabled: true,
            rescale: true
        },
        axis: {
            x: {
                type: 'category',// this needed to load string x value
                tick: {
                    rotate: 75,
                    multiline: false
                },
                height: 160
            }
        }
    });

    agencyStatisticsSpinner.stop();
});
