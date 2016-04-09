# City Feedback Hub

[![Build Status](http://94.237.25.111:8080/job/city-feedback-hub/badge/icon)](http://94.237.25.111:8080/job/city-feedback-hub)

Link to the latest development version: <http://feedback.hel.ninja>  

[API documentation](https://github.com/hep7agon/city-feedback-hub/wiki) 

## Description

City Feedback Hub (CFH) is a Aalto software development project made for the City of Helsinki. The aim of this project is to create a new inspiring web service for the citizens to send and browse existing feedbacks using the [Open311 API](http://dev.hel.fi/apis/open311/) already in use in Helsinki. This website tries to encourage citizens to participate in improving their neighbourhood. 

CFH provides means to report issues to the city by simple to use feedback form wizard. The user can give the location of the issue, basic info and also attach images to help describe the issue. CFH also provides ways to browse existing feedbacks with various filters. There is also a map ([Leaflet](http://leafletjs.com) view which shows what is happening around. The map shows both individual feedbacks and also provides a *heatmap* to easily identify "hot" areas. There are also pages to show various statistical information and charts.

One of the main criteria was to make the website responsive so that it can be easily used with mobile phones and other portable devices. This has been achieved with [Bootstrap 3](http://getbootstrap.com).

## Installation for developers

1. Install [Python 3](https://www.python.org)
2. Install [PostgreSQL](http://www.postgresql.org)
3. Fire up PostgreSQL and create database: `createdb cfh`
4. Clone this repository
5. Create a new virtualenv (not mandatory, but good practice)
6. Enter into the virtualenv
7. Install requirements: `pip install -r requirements.txt`
8. Migrate: `python manage.py migrate`
9. Load sample data: `python manage.py loaddata real_feedbacks.json`
10. Start local Django server: `python manage.py runserver`
11. Open <http://localhost:8000>

## Development

CFH is a Django application. The application is divided into two apps: frontend, which handles UI and all client side logic, and API, which handles the Feedback and statistic APIs, data synchronization etc. DB layout is defined in `api/models.py`. Client side logic is defined in `frontend/views.py` and the page layout is defined in various templates in `frontend/templates/`. Client URL scheme is in a typical place `frontend/urls.py`. Various Javascript/jQuery scripts are stored in `frontend/static/`.

The default configuration assumes that the software is using the Helsinki Open311 API but it is possible to use CFH as a standalone feedback system with some modifications.

## Running tests

Both frontend and backend has unit tests available. Unit tests can be found in `api/tests/` and in `frontend/tests.py`. Nose test package is also used to get code coverage statistics. Unit tests can be run the usual way: 

`python manage.py test` 

By default it also checks code coverage.

## Custom Django Commands
There are also custom commands that can be run with: 

	python manage.py [command] [--param1] [--param2=value]

##### calcestimation
Calculate and fill expected_datetime field for feedbacks which have this field empty

##### purge_mediafiles
Deleted unneeded temporary media files and MediaFile objects from MEDIA_ROOT

Available options:

- `force`: Prevent asking for confirmation of deletion.
- `silent`: Don't display info about deletion and files.
- `days`: Script will delete files which are more than DAYS days old. Default is 1.

##### pushdata
Push new feedbacks to Open311 and save their service_request_id

##### reversegeocoding
Push new feedbacks to Open311 and save their service_request_id

##### syncdata
Read and save data from Open311 Server provided in settings.py. To write feedbacks to Open311 see \'pushdata\' command.

##### syncservices
Read and save service data from Open311 Server provided in settings.py.


