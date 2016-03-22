# City Feedback Hub

Link to the latest development version: <http://feedback.hel.ninja>

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

[![Build Status](http://94.237.25.111:8080/job/city-feedback-hub/badge/icon)](http://94.237.25.111:8080/job/city-feedback-hub)