(function (m, config, gettext, IssueUtils) {
  var bootstrapFormField = IssueUtils.bootstrapFormField;
  var services = m.request({
    method: 'GET',
    url: config.api_root + 'services.json',
    initialValue: [],
  });
  var map = null;
  var mapMarkerGroup = null;

  function initiateSearch() {
    var params = {
      extensions: 'citysdk',
      page: state.page(),
    };
    if (state.search()) {
      params.search = state.search();
    }
    if (state.service()) {
      params.service_code = state.service();
    }
    if (state.bbox()) {
      params.bbox = state.bbox();  // already in string format
    }
    if (state.circle()) {
      Object.assign(params, state.circle()); // unpack lat/lng/radius into params
    }
    state.searching(true);
    m.request({
      method: 'GET',
      url: config.api_root + 'requests.json',
      data: params,
      initialValue: state.results(),  // Use the previous value while we wait
      background: true,
      extract: function (xhr) {
        var results = JSON.parse(xhr.responseText);
        return {
          results: results,
          pageCount: xhr.getResponseHeader('X-Page-Count'),
          resultCount: xhr.getResponseHeader('X-Result-Count'),
        };
      },
      deserialize: function (value) {
        return value;  // already handled in extract
      },
    }).then(function (res) {
      state.searching(false);
      state.results(res);
      updateMapWithResults(res.results);
      m.redraw(true);
    });
  }

  var initiateNewSearchSoon = IssueUtils.debounce(function () {
    state.page(1);
    initiateSearch();
  }, 150);

  var state = {
    search: IssueUtils.observeProp(m.prop(''), initiateNewSearchSoon),
    service: IssueUtils.observeProp(m.prop(''), initiateNewSearchSoon),
    bbox: IssueUtils.observeProp(m.prop(null), initiateNewSearchSoon),
    circle: IssueUtils.observeProp(m.prop(null), initiateNewSearchSoon),
    page: IssueUtils.observeProp(m.prop(1), initiateSearch),
    searching: m.prop(false),
    results: m.prop(null),
  };

  var getServiceSelectOptions = IssueUtils.purify(function (serviceList) {
    return [{value: '', text: gettext('any service')}].concat(serviceList.map(function (s) {
      return {value: s.service_code, text: s.service_name || s.service_code};
    })).map(function (opt) {
      return m('option', {value: opt.value, key: opt.value}, opt.text);
    });
  }, function () {
    return services();
  });

  function updateMapWithResults(issues) {
    if (!map) {
      return;
    }
    var group = new L.FeatureGroup();
    var latLngs = [];
    issues.filter(function (issue) {
      return issue.lat && issue.long;
    }).forEach(function (issue) {
      var latLng = new L.LatLng(issue.lat, issue.long);
      latLngs.push(latLng);
      var marker = L.marker(latLng);
      var markerContent = ([
        (issue.description).replace(/</g, '&lt;').replace(/>/g, '&gt;'),
        "<br>",
        gettext("Show").link("#" + issue.service_request_id)
      ]).join("");
      marker.bindPopup(markerContent, {showOnMouseOver: true});
      group.addLayer(marker);
    });

    if (mapMarkerGroup) {
      map.removeLayer(mapMarkerGroup);
      mapMarkerGroup = null;
    }
    map.addLayer(group);
    if (latLngs.length) {
      var bounds = new L.LatLngBounds(latLngs);
      bounds.pad(0.05);
      map.fitBounds(bounds);
    }
    mapMarkerGroup = group;
  }

  function getBaseFilterRow() {
    return m('.row', [
      m('.col-md-12', bootstrapFormField({
        type: 'search',
        id: 'search',
        bind: state.search,
        label: gettext('Search for issues'),
        placeholder: gettext('Search for text...'),
      })),
      m('.col-md-12', bootstrapFormField({
        tag: 'select',
        id: 'service',
        bind: state.service,
        label: gettext('Select a service'),
        children: getServiceSelectOptions(),
      })),
    ]);
  }

  function getGeoFilterPanel() {
    return m('div', [
      m('.btn-group', [
        m('a.btn.btn-default', {
          href: '#',
          onclick: function () {
            map.startLittlePen('box');
          },
        }, gettext('Search by box')),
        m('a.btn.btn-default', {
          href: '#',
          onclick: function () {
            map.startLittlePen('circle');
          },
        }, gettext('Search by circle')),
        m('a.btn.btn-default', {
          href: '#',
          onclick: function () {
            map.clearLittlePen();
            state.bbox(null);
            state.circle(null);
          },
        }, gettext('Clear search')),
      ]),
      m('div', {
        config: IssueUtils.getLeafletSetup(function (context) {
          map = context.map;

          map.on('littlePenSelectBox', function (args) {
            state.circle(null);
            state.bbox(args.bounds.toBBoxString());
          });
          map.on('littlePenSelectCircle', function (args) {
            state.bbox(null);
            state.circle({
              lat: args.center.lat,
              long: args.center.lng,
              radius: args.radius,
            });
          });
        }),
      }),
    ]);
  }

  function tryLocalizeDateTime(val) {
    try {
      return new Date(val).toLocaleString();
    } catch (e) {
      return val;
    }
  }

  function renderResult(result) {
    var ea = result.extended_attributes || {};
    var props = {
      key: result.service_request_id,
      id: result.service_request_id,
    };
    return m('div.result', props, [
      m('div.row', [
        m('div.col-md-8', [
          (ea.title ? m('h2', ea.title) : null),
          m('p', result.description),
          (result.status_notes ? m('blockquote', [
            result.status_notes,
            (result.agency_responsible ? m('footer', result.agency_responsible) : null),
          ]) : null),
          (result.address ? m('.text-muted', result.address) : null),
        ]),
        m('div.col-md-4', [
          gettext('Sent ') + tryLocalizeDateTime(result.requested_datetime),
          gettext('Updated ') + tryLocalizeDateTime(result.updated_datetime),
          gettext('Status ') + result.status,
        ].map(function (t) {
          return (t ? m('div', t) : null);
        })),
      ]),
      m('hr'),
    ]);
  }

  function getPaginator(results, id) {
    if (results.pageCount <= 1) return;
    var cacheKey = '_mith_' + id;
    var paginator = results[cacheKey];
    if (!paginator) {
      var range = [];
      for (var page = 1; page <= parseInt(results.pageCount); page++) {
        range.push(page);
      }
      paginator = m('ul.pagination', {id: id}, range.map(function (page) {
        return m(
          'li' + (state.page() === page ? '.active' : ''),
          m('a', {
            href: '#' + id,
            onclick: function (event) {
              results[cacheKey] = null; // Uncache
              state.page(page);
              event.preventDefault();
            },
          }, page)
        );
      }));
      results[cacheKey] = paginator;
    }
    return paginator;
  }

  function getResults() {
    var results = state.results();
    if (!results) {
      return null;
    }
    return m('div.results-container', [
      m('nav', getPaginator(results, 'top-nav')),
      (results.results || []).map(function (result) {
        return (result._mithril || (result._mithril = renderResult(result)));
      }),
      m('nav', getPaginator(results, 'btm-nav')),
    ]);
  }

  function view() {
    return m('div', [
      m('.well', [
        m('.row', [
          m('.col-md-4', getBaseFilterRow()),
          m('.col-md-8', getGeoFilterPanel()),
        ]),
      ]),
      getResults(),
    ]);
  }

  m.mount(document.getElementById('browse-app-container'), {view: view});
  initiateSearch();
}(window.m, window.config, window.gettext, window.IssueUtils));
