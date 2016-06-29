# Issue Reporting

[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)

Based on [hep7agon/city-feedback-hub](https://github.com/hep7agon/city-feedback-hub). Thanks!

## Description

This project implements a civic issue reporting system with a [GeoReport v2](http://wiki.open311.org/GeoReport_v2/) API.

This repository may be used either as a standalone GeoReport V2 API server,
or its components may be used as Django applications.

When installing via PyPI or `setup.py`, the standalone project is _not_ available, but the Django applications are.

## Requirements

* Python 3
* Any database supported by Django. PostgreSQL with the PostGIS extension is preferrable.
  * Non-GIS-enabled databases will work too, but with degraded performance and/or capabilities.

## Usage as a standalone project

### Setup

The project is a regular Django project, so no thoroughly special steps should need to be taken.

* Set up a Python 3 virtualenv
* `pip install -e requirements.txt` in the virtualenv
* Set up a database
* Run using your favorite Python application server

### Configuration

The `cfh` project is configured via environment variables, described below.

* `DEBUG`: enable debug/development mode and set sane development defaults.
* `SECRET_KEY`: the Django secret key. Must be set when not `DEBUG`ging.
* `DATABASE_URL`: an URL pointing to the SQL database for the project.
* `LANGUAGES`: a comma-separated list of ISO 639-1 language codes to enable. Defaults to `en,fi`
* `MEDIA_ROOT`: The root filesystem directory for media uploads
* `STATIC_ROOT`: The root filesystem directory where static files are gathered into

All of the Django settings described below are also available as equivalently
named environment variables for the standalone project.

## Development

* Install dependencies from both `requirements.txt` and `requirements-dev.txt`.
* If the `DEBUG` envvar is truthy, sane development defaults are automatically inferred.
* Use `pip-tools` to manage the two requirements files.

### Running tests

Py.test is used as the test runner. Just run `py.test` (with `--cov` for coverage)

## Importing issues

You may wish to import some issues from a pre-existing GeoReport V2 server to test your installation against.

For instance, to use the City of Helsinki's `palautews` service for this, use Django's shell to:

```python
from issues.sync.down import update_from_georeport_v2_url
update_from_georeport_v2_url("https://asiointi.hel.fi/palautews/rest/v1/requests.json")
```
## Django settings

* `ISSUES_DEFAULT_MODERATION_STATUS`:
  * Set to `unmoderated` to set newly created issues as unmoderated, which makes them not appear in lists
    before set to public.
* `ISSUES_GEOMETRY_SRID`:
  * The SRID to use for the geometry fields in `issues_geometry`. Defaults to 4326 (WGS84).
