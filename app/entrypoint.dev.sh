#!/bin/sh

echo "Development app start"

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


#Run web server
python manage.py runserver 0.0.0.0:$WEB_PORT

exec "$@"