#!/bin/sh

echo "Production app start"

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi



#Run web server
gunicorn config.wsgi:application --bind web:$WEB_PORT

exec "$@"