"use strict";

var HelsinkiCoord = {lat: 60.17067, lng: 24.94152};
// Bounds from Helsinki's Servicemap code (https://github.com/City-of-Helsinki/servicemap/)
var bounds = L.bounds(L.point(-548576, 6291456), L.point(1548576, 8388608));

var crs = function() {
    var bounds, crsName, crsOpts, originNw, projDef;
    crsName = 'EPSG:3067';
    projDef = '+proj=utm +zone=35 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs';
    bounds = L.bounds(L.point(-548576, 6291456), L.point(1548576, 8388608));
    originNw = [bounds.min.x, bounds.max.y];
    crsOpts = {
        resolutions: [8192, 4096, 2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25, 0.125],
        bounds: bounds,
        transformation: new L.Transformation(1, -originNw[0], -1, originNw[1])
    };
    return new L.Proj.CRS(crsName, projDef, crsOpts);
}
var map = L.map('map', {
    crs : crs(),
    zoomControl: false
}).setView([HelsinkiCoord.lat, HelsinkiCoord.lng], 11);

L.tileLayer("http://geoserver.hel.fi/mapproxy/wmts/osm-sm/etrs_tm35fin/{z}/{x}/{y}.png", {
    attribution: 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
    maxZoom: 18,
    continuousWorld: true,
    tms: false
}).addTo(map);

map.addControl(L.control.zoom({ position : 'topright' }));

L.easyButton('<span class="glyphicon glyphicon-map-marker"></span>', function(){
    getUserLocation();
}, {position: 'topright'}).addTo(map);

function getUserLocation(e) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var newLocation = L.latLng(position.coords.latitude, position.coords.longitude);
            //userLocation.setLatLng(newLocation);
            //storeLocation(newLocation);
            map.panTo(newLocation);
        }.bind(this));
    }
    else {
        console.error("Geolocation is not supported by this browser.");
    }
}

var userLocation;

function addMarker(e){
    // Add marker to map at click location; add popup window
    if ( typeof(userLocation) === 'undefined' )
	{
    	userLocation = new L.marker(e.latlng, {draggable:true}).addTo(map);
    }
    else 
	{
		userLocation.setLatLng(e.latlng);         
	}
}

 function onToggleMenu(){
    $("#sidebar-wrapper").toggleClass("toggled");
    $("#toggleButton").toggleClass("toggled");
    $("#toggleButtonIcon").toggleClass("glyphicon-chevron-left glyphicon-chevron-right");    
}