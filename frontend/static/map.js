"use strict";

var markers = [];
var markerCoordinates = [];
var markersLayer = L.layerGroup();
var heatLayer = null;

moment.locale('fi');

$(document).ready(function() {
    getData({"status" : "open"}, true);
});

function getData(params, markersVisible) {
    $.getJSON("/api/v1/requests.json/?extensions=true", params, function (data) {

        if (markers.length > 0) {
            for (var i = 0; i < markers.length; i++) {
                map.removeLayer(markers[i]);
            }
        }

        if (markerCoordinates.length > 0) {
            markerCoordinates.length = 0;
        }

        $.each(data, function (key, feedback) {

            // specify popup options 
            var customOptions =
                {
                    'maxWidth': '300',
                    'className' : 'custom'
                }

            var popupContent = "";

            popupContent += "<h4 id=\"feedback_title\"></h4>" +
                "<div id=\"feedback_service_name\"></div>" +
                "<div id=\"feedback_requested_datetime\"></div>" +
                "<p id=\"feedback_description\"></p>" +
                "<a id=\"feedback_details\" href=\"\"></a>";

            var marker = L.marker([feedback.lat, feedback.long], {icon: feedback_icon}).bindPopup(popupContent, customOptions).addTo(markersLayer);
            marker.feedback = feedback;
            markerCoordinates.push([feedback.lat, feedback.long]);
            marker.on('click', function(e) {
                if (highlight !== null) {
                    // is highlighted, store id of marker
                    var id = highlight._leaflet_id;
                }

                removeHighlight();

                if (id !== marker._leaflet_id) {
                    // Set highlight icon
                    marker.setIcon(highlight_icon);
                    // Assign highlight
                    highlight = marker;
                }

                $('#feedback_title').text(e.target.feedback.extended_attributes.title);
                $('.feedback_list_vote_badge').text(e.target.feedback.vote_counter);
                $('.feedback_list_vote_icon').attr("id", e.target.feedback.service_request_id);
                $('#feedback_service_name').text("Aihe: " + e.target.feedback.service_name);
                var datetime = moment(e.target.feedback.requested_datetime).fromNow();
                $('#feedback_requested_datetime').text("Lisätty: " + datetime);
                var len = 135;
                var desc = e.target.feedback.description;
                var trunc_desc = desc.substring(0, len)  + "...";
                $('#feedback_description').text(trunc_desc);
                var feedback_url = "/feedbacks/" + e.target.feedback.id;
                $('#feedback_details').text("Lisää");
                $('#feedback_details').attr("href", feedback_url);
                $('#feedback_info').css("visibility", "visible");
                
            });
            markers.push(marker);
        });
    });
    if (markersVisible) {
        showMarkers(markersVisible);
    }
}

var center_icon = L.MakiMarkers.icon({icon: "circle", color: "#62c462", size: "l"});
var feedback_icon = L.MakiMarkers.icon({icon: "circle", color: "#0072C6", size: "m"});
var highlight_icon = L.MakiMarkers.icon({icon: "circle", color: "#FFC61E", size: "m"});

// Variable to keep track of highlighted marker
var highlight = null;

// Function for removing highlight 
function removeHighlight () {
    // Check for highlight
    if (highlight !== null) {
        // Set default icon
        highlight.setIcon(feedback_icon);
        // Unset highlight
        highlight = null;
        $('#feedback_info').css("visibility", "hidden");
    }
}


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
    crs: crs(),
    zoomControl: false
}).setView([HelsinkiCoord.lat, HelsinkiCoord.lng], 11);

// Automatically fwetch user location and center
getUserLocation();

L.tileLayer("http://geoserver.hel.fi/mapproxy/wmts/osm-sm/etrs_tm35fin/{z}/{x}/{y}.png", {
    attribution: 'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
    maxZoom: 18,
    continuousWorld: true,
    tms: false
}).addTo(map);

map.addControl(L.control.zoom({position: 'topright'}));

L.easyButton('<span class="glyphicon glyphicon-map-marker"></span>', function () {
    getUserLocation();
}, {position: 'topright'}).addTo(map);

function getUserLocation(e) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var newLocation = L.latLng(position.coords.latitude, position.coords.longitude);
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

function showMarkers(show) {
    if (show) {
        map.addLayer(markersLayer);
    }
    else
    {
        if (map.hasLayer(markersLayer)) {
            map.removeLayer(markersLayer);
        } 
    }
}

function showHeatmap(show) {
    if (show) {
        if(heatLayer)
            map.removeLayer(heatLayer);

        heatLayer = L.heatLayer(markerCoordinates, {minOpacity: 0.4, maxZoom: 18}).addTo(map);
    }
    else
    {
        if(heatlayer)
            map.removeLayer(heatlayer);
    }
}

function onToggleMenu() {
    $("#sidebar-wrapper").toggleClass("toggled");
    $("#toggleButton").toggleClass("toggled");
    $("#toggleButtonIcon").toggleClass("glyphicon-chevron-left glyphicon-chevron-right");
}