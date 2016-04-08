
        function humanize(value) {
            return Math.floor(value / 86400) + 'pv ' + Math.floor((value % 86400) / 3600) + 'h';
        };

       


        $.getJSON("/api/v1/statistics/services/", function (data) {
            var services = ['x'];
            var total = ['kaikki'];
            var closed = ['suljetut'];
            var fixing_time_in_hours = ['Korjausaika päivissä ja tunneissa'];
            $.each(data, function (key, item) {
                services.push(item.service_name);
                total.push(item.total);
                closed.push(item.closed);
                fixing_time_in_hours.push(item.median_sec)
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
                    type: 'bar',
                },
                axis: {
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

            c3.generate({
                bindto: '#timeStatistics',
                data: {
                    x: 'x',
                    columns: [
                        services,
                        fixing_time_in_hours
                    ],
                    type: 'bar',
                    labels: {
                        format: humanize
                    }
                },
                axis: {
                    y: {
                        tick: {
                            format: function humanize(value) {
                                return Math.round(value / 86400);
                            }
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
                    right: 12,
                },
                data: {
                    x: 'x',
                    columns: [
                        agencies,
                        total,
                        closed
                    ],
                    type: 'bar',
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
        });
