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


  // From Underscore.
  var debounce = function (func, wait, immediate) {
    var timeout;
    return function () {
      var context = this, args = arguments;
      var later = function () {
        timeout = null;
        if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
    };
  };

  /**
   * Instrument a mithril prop with support for a change listener.
   * @param prop A mithril-prop-like object.
   * @param valueWillChange {function} A function that will be called when the value is about to change.
   * @returns {prop}
   */
  var observeProp = function (prop, valueWillChange) {
    var iProp = function iProp() {
      var current = prop();
      if (arguments.length === 0) return current;
      var val = arguments[0];
      if (current !== val) {
        if (valueWillChange) {
          valueWillChange(val, current);
        }
        prop(val);
      }
      return val;
    };
    iProp.toJSON = function () {
      return prop();
    };
    return iProp;
  };

  /**
   * Return a cached version of the pure function `cachee`.
   * The cachee function will be called (whenever necessary) with the retval of `dependency`.
   * The returned function does not accept any arguments.
   */
  var purify = function (cachee, dependency) {
    var lastArg, lastValue;
    return function () {
      var arg = dependency();
      if (arg === lastArg) {
        return lastValue;
      }
      lastArg = arg;
      lastValue = cachee(arg);
      return lastValue;
    };
  };

  return {
    bootstrapFormField: bootstrapFormField,
    debounce: debounce,
    getLeafletSetup: getLeafletSetup,
    observeProp: observeProp,
    purify: purify,
  };
}(window.L, window.m, window.config));
