window.IssueUtils = (function (L, m, config) {
  function bootstrapFormField(opts) {
    opts = opts || {};
    var tag = (opts.tag || 'input');
    delete opts.tag;
    if (opts.bind) {   // auto-bind
      opts.oninput = opts.onchange = m.withAttr('value', opts.bind);
      if (!('value' in opts)) {
        opts.value = opts.bind();
      }
      delete opts.bind;
    }
    var children = (opts.children || []);
    delete opts.children;
    return m(
      '.form-group',
      {key: opts.id}, [
        (opts.label ? m('label', {for: opts.id}, opts.label) : null),
        m(tag + '.form-control', Object.assign({id: opts.id}, opts), children),
      ]
    );
  }

  /**
   * Return a Mithril setup function that will set up Leaflet in a child div of the element.
   * The given `configurator` callable is called exactly once, and is passed the Mithril context.
   * @param configurator a configuration function (see above).
   */
  function getLeafletSetup(configurator) {
    return function setupLeaflet(element, isInitialized, context) {
      if (!isInitialized) {
        var wrapper = context.wrapper = document.createElement('div');
        wrapper.className = 'map-container';
        element.appendChild(wrapper);
        var map = context.map = L.map(wrapper, {
          center: config.map_settings.center,
          zoom: 14,
        });
        L.tileLayer(config.map_settings.tileUrl, {
          attribution: config.map_settings.attribution,
        }).addTo(map);
        if (configurator) {
          configurator(context, element);
        }
      }
    };
  }

  return {
    bootstrapFormField: bootstrapFormField,
    getLeafletSetup: getLeafletSetup,
  };
}(window.L, window.m, window.config));
