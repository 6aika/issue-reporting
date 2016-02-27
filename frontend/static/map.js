"use strict";

var HelsinkiCoord = {lat: 60.17067, lng: 24.94152};

var map = L.map('map').setView([HelsinkiCoord.lat, HelsinkiCoord.lng], 14);


// Try to get CartoDB's Positron/light basemap into use
// https://cartodb.com/basemaps/
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
    maxZoom: 18,
}).addTo(map);
map.on('click', addMarker);


/*
// Add basemap and map settings.
L.tileLayer( 'http://{s}.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright" title="OpenStreetMap" target="_blank">OpenStreetMap</a> contributors | Tiles Courtesy of <a href="http://www.mapquest.com/" title="MapQuest" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png" width="16" height="16">',
    subdomains: ['otile1','otile2','otile3','otile4'],
    minZoom: 11,
    maxZoom: 18,
}).addTo(map);
*/
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

 