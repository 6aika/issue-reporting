/**
 * LittlePen is an opt-in box-and-circle-drawing addon for Leaflet maps.
 * Heavily, ah, inspired by `L.Map.BoxZoom`.
 */
(function (L) {
  L.Map.mergeOptions({littlePen: true});

  L.Map.LittlePen = L.Handler.extend({
    initialize: function (map) {
      this._map = map;
      this._container = map._container;
      this._mode = null;  // null/"box"/"circle"
      this._layer = null;
      var self = this;
      map.startLittlePen = function (mode) {
        self._finish();
        self._mode = mode;
        self._map.dragging.disable();
      };
      map.clearLittlePen = function () {
        self.clean();
      };
      map.getLittlePenMode = function () {
        return self._mode;
      };
    },

    addHooks: function () {
      L.DomEvent.on(this._container, 'mousedown', this._onMouseDown, this);
    },

    removeHooks: function () {
      L.DomEvent.off(this._container, 'mousedown', this._onMouseDown, this);
    },

    moved: function () {
      return this._moved;
    },

    _resetState: function () {
      this._moved = false;
    },

    clean: function () {
      if (this._layer) {
        this._layer.removeFrom(this._map);
        this._layer = null;
      }
    },

    _onMouseDown: function (e) {
      if (!this._mode) {  // User has to prime this
        return false;
      }
      if (e.shiftKey) {  // Shift-zooming is boxzoom's territory
        return false;
      }
      if (!(e.which === 1 || e.button !== 1)) {  // Wrong button?
        return false;
      }

      this._resetState();

      L.DomUtil.disableTextSelection();
      L.DomUtil.disableImageDrag();

      this._startLatLng = this._map.containerPointToLatLng(
        this._map.mouseEventToContainerPoint(e)
      );

      L.DomEvent.on(document, {
        contextmenu: L.DomEvent.stop,
        mousemove: this._onMouseMove,
        mouseup: this._onMouseUp,
        keydown: this._onKeyDown,
      }, this);
    },

    _onMouseMove: function (e) {
      this._latLng = this._map.containerPointToLatLng(
        this._map.mouseEventToContainerPoint(e)
      );
      var bounds = new L.LatLngBounds(this._latLng, this._startLatLng);
      if (!this._moved) {
        this._moved = true;
        this.clean();
        switch (this._mode) {
          case 'box':
            this._layer = L.rectangle(bounds);
            break;
          case 'circle':
            this._layer = L.circle(this._startLatLng, 0);
            break;
          default:
            throw new Error('not implemented');
        }
        this._layer.addTo(this._map);
      }

      switch (this._mode) {
        case 'box':
          this._layer.setBounds(bounds);
          break;
        case 'circle':
          this._layer.setRadius(this._startLatLng.distanceTo(this._latLng));
          break;
        default:
          throw new Error('not implemented');
      }

    },

    _finish: function () {
      this._mode = null;
      this._map.dragging.enable();

      L.DomUtil.enableTextSelection();
      L.DomUtil.enableImageDrag();

      L.DomEvent.off(document, {
        contextmenu: L.DomEvent.stop,
        mousemove: this._onMouseMove,
        mouseup: this._onMouseUp,
        keydown: this._onKeyDown,
      }, this);
    },

    _onMouseUp: function () {
      if (!(this._layer && this._mode)) {
        return;
      }
      var mode = this._mode;
      this._finish();
      switch (mode) {
        case 'box':
          this._map.fire('littlePenSelectBox', {bounds: this._layer.getBounds()});
          break;
        case 'circle':
          this._map.fire('littlePenSelectCircle', {
            center: this._layer.getLatLng(),
            radius: this._layer.getRadius(),
          });
          break;
      }
      setTimeout(L.bind(this._resetState, this), 0);
    },

    _onKeyDown: function (e) {
      if (e.keyCode === 27) {
        this._finish();
      }
    },
  });

  L.Map.addInitHook('addHandler', 'littlePen', L.Map.LittlePen);

}(window.L));
