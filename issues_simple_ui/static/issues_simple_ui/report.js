(function (L, m, config, gettext, IssueUtils) {
  var bootstrapFormField = IssueUtils.bootstrapFormField;
  var services = m.request({
    method: 'GET',
    url: config.api_root + 'services.json',
  });
  var state = {
    service: m.prop(null),
    description: m.prop(''),
    title: m.prop(''),
    location: m.prop(null),
    address: m.prop(''),
    first_name: m.prop(''),
    last_name: m.prop(''),
    phone: m.prop(''),
    email: m.prop(''),
    attachments: m.prop([]),
    status: m.prop(null),  // null / submitting / submitted
    createdRequest: m.prop(null),
  };

  function setupLeaflet(context) {
    var map = context.map;
    context.mapMarker = null;
    map.on('click', function (e) {
      if (!context.mapMarker) {
        context.mapMarker = L.marker(e.latlng);
        context.mapMarker.addTo(map);
      }
      context.mapMarker.setLatLng(e.latlng);
      state.location({lat: e.latlng.lat, long: e.latlng.lng});
      map.panTo(e.latlng);
    });
  }

  function contactInfoBlock() {
    return m('div', [
      m('h2', gettext('Contact Information')),
      m('p', gettext('If you\'d like, you can enter your contact details. These are not public.')),
      m('.row', [
        bootstrapFormField({
          id: 'first_name',
          bind: state.first_name,
          placeholder: gettext('Your First Name'),
        }),
        bootstrapFormField({
          id: 'last_name',
          bind: state.last_name,
          placeholder: gettext('Your Last Name'),
        }),
        bootstrapFormField({
          id: 'phone',
          bind: state.phone,
          placeholder: gettext('Your Phone Number'),
        }),
        bootstrapFormField({
          id: 'email',
          bind: state.email,
          type: 'email',
          placeholder: gettext('Your Email Address'),
        }),
      ].map(function (f) {
        return m('div.col-md-3', {key: f.attrs.key}, f);
      })),
    ]);
  }

  function locationBlock() {
    return m('div', [
      m('h2', gettext('Location')),
      m('p', gettext('Tap on the map to choose a point and/or add an address.')),
      m('div', {
        config: IssueUtils.getLeafletSetup(setupLeaflet),
      }),
      bootstrapFormField({
        id: 'address',
        bind: state.address,
        placeholder: gettext('You may also enter an address here.'),
      }),
    ]);
  }

  function attachmentsBlock() {
    return m('div', [
      m('h2', gettext('Attachments')),
      m('p', gettext('You can attach a file to your report.')),
      m('input', {
        type: 'file',
        multiple: true,
        onchange: function () {
          state.attachments([].slice.call(this.files));
        },
      }),
    ]);
  }

  function validate() {
    var errors = [];
    if (!state.description().trim()) {
      errors.push(gettext('Please describe your issue.'));
    }
    var locationReq = config.service_location_req;
    var hasAddress = !!(state.address().trim());
    var hasLocation = !!state.location();
    if (locationReq == 'address' && hasAddress) {
      errors.push(gettext('Please state the address for your issue.'));
    }
    if (locationReq == 'coords_or_address' && !(hasAddress || hasLocation)) {
      errors.push(gettext('Please state the address or location for your issue.'));
    }
    var email = state.email().trim();
    if (email.length && !(/^.+@.+\..+$/.test(email))) {
      errors.push(gettext('Please enter a valid email or none at all.'));
    }
    return errors;
  }

  function buildSubmissionData() {
    var data = new FormData();
    var simpleData = {
      address: state.address().trim(),
      description: state.description().trim(),
      email: state.email().trim(),
      first_name: state.first_name().trim(),
      last_name: state.last_name().trim(),
      phone: state.phone().trim(),
      service_code: state.service().service_code,
      title: state.title().trim(),
      csrfmiddlewaretoken: config.csrf_token,  // May not exist
    };
    if (state.location()) {
      Object.assign(simpleData, state.location());
    }
    for (var key in simpleData) {
      var value = simpleData[key];
      if (value) {
        data.append(key, value);
      }
    }
    (state.attachments() || []).forEach(function (file) {
      data.append('media', file);
    });
    return data;
  }

  function submit(event) {
    event.preventDefault();
    var errors = validate();
    if (errors && errors.length) {
      alert(errors.join('\n'));
      return false;
    }
    var data = buildSubmissionData();
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;

      if (xhr.status == 201) {
        state.status('submitted');
        state.createdRequest(JSON.parse(xhr.responseText)[0]);
      } else {
        state.status(null);
        alert('Oops!\n' + xhr.responseText);
      }
      m.redraw();
    };
    xhr.open('POST', config.api_root + 'requests.json?extensions=citysdk,media', true);
    xhr.send(data);
    state.status('submitting');
  }

  function view() {
    var service = state.service();
    if (service === null) {
      return m('div', [
        gettext('Select the service your issue regards.'),
        m('ul', (services() || []).map(function (service) {
          return m(
            'li',
            {key: service.service_code},
            m('a', {
              href: '#',
              onclick: function () {
                state.service(service);
              },
            }, service.service_name || service.service_code),
            (service.description ? m('div', service.description) : null)
          );
        })),
      ]);
    }
    if (state.status() === 'submitted') {
      var req = state.createdRequest();
      var ty = config.thank_you;
      return m('div', [
        m('h2', ty.title || gettext('Thank you!')),
        m('p', m.trust(ty.content || gettext('Your report has been submitted.'))),
        m('p', m.trust(gettext('The ID of your request is <b>{code}</b>.').replace('{code}', req.service_request_id))),
      ]);
    }
    return m('form', [
      m('div', [
        gettext('Service: ') + service.service_name,
        ' ',
        m('a.btn.btn-default.btn-xs', {
          href: '#', onclick: function () {
            state.service(null);
          },
        }, gettext('Change...')),
      ]),
      m('hr'),
      bootstrapFormField({
        id: 'description',
        label: gettext('Please describe your issue'),
        tag: 'textarea',
        bind: state.description,
      }),
      bootstrapFormField({
        id: 'title',
        label: gettext('Give the issue an optional title'),
        bind: state.title,
      }),
      locationBlock(),
      contactInfoBlock(),
      attachmentsBlock(),
      m('hr'),
      (
      state.status() == 'submitting' ?
          m('div', m('.progress', m('.progress-bar.progress-bar-striped.active', {style: 'width: 100%'}))) :
          m('button.btn-lg.btn-primary.btn-block', {
            onclick: submit,
          }, gettext('Submit'))
      ),
    ]);
  }

  m.mount(document.getElementById('report-form-container'), {view: view});
}(window.L, window.m, window.config, window.gettext, window.IssueUtils));
