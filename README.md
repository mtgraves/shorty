# Shorty

URL shortener/redirect utility that I built a few years ago and just now pushed up here.  Needs the auth flow reworked, as it was originally built to utilize an IDP for AuthN that is not publicly available.

## The details
 - `flask` web framework for the backend
 - `jinja2` templating for the frontend
 - `mariadb` database with `flask-sqlalchemy` to utilize the `SQLAlchemy` ORM
 - built to be provisioned and run on a `centos` machine hosted locally using `vagrant`
 - served up by `gunicorn` as a `systemd` service behind `nginx` as a reverse proxy
