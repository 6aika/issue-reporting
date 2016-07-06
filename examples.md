Examples
========

These examples use [Httpie](https://github.com/jkbrzt/httpie) command line application.

POST a service request 
----------------------

Standard Georeport V2 in JSON-format
------------------------------------

request-post.json:
```json
{
    "description": "Trash bin is full.",
    "service_code": "180",
    "first_name": "Heikki",
    "last_name": "Helsinkiläinen",
    "lat": 60.1893135,
    "long": 25.0081830
}
```

`http -v POST 'https://open311-sandbox.6aika.fi/api/georeport/v2/requests.json' < request-post.json`

CitySDK and Geometry extension data
-----------------------------------

request-post-geo.json:
```json
{
    "title": "Geometry example",
    "service_code": "180",
    "description": "Too much snow on the bike track at Verkatehtaanpuisto park.",
    "first_name": "Geo",
    "last_name": "Guy",
    "geometry": {
        "type": "LineString",
        "coordinates": [
          [24.98294, 60.21358],
          [24.98256, 60.21312],
          [24.98271, 60.21276],
          [24.98353, 60.21214],
          [24.98340, 60.21171],
          [24.98281, 60.21133]
        ]
    }
}
```

`http -v POST 'https://open311-sandbox.6aika.fi/api/georeport/v2/requests.json?extensions=citysdk,geometry' < request-post-geo.json`

Note: if you set `extensions=true` all installed extensions are available automatically. 

Upload a photo, multipart POST
------------------------------

```shell
http -v -f POST 'https://open311-sandbox.6aika.fi/api/georeport/v2/requests.json?extensions=citysdk,media,geometry' \
    service_code=171 title='Multipart geometry' description="Multipart" \
    email=Email@addre.ss first_name=First last_name=Last phone=Phone \
    geometry='{"type":"LineString","coordinates": [[24.98294,60.21358],[24.98256,60.21312],[24.98271,60.21276],[24.98353,60.21214],[24.98340,60.21171],[24.98281,60.21133]]}' \ 
    media@~/picture.jpg media@~/Desktop/picture.png
```
