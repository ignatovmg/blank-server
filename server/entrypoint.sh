#!/bin/sh

# wait for the database
if [ "$LOCAL_DB_NAME" = "brikard" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $LOCAL_DB_HOST 5432; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Add changes to the database
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Copy all the static file to one directory (specified in settings.py)
python manage.py collectstatic --no-input

# Create superuser and an anonymous user
python manage.py shell -c '''
from django.contrib.auth.models import User

if not User.objects.filter(username="admin").exists(): 
	User.objects.create_superuser(username="admin", password="admin", email="")

if not User.objects.filter(username="anon").exists():
	User.objects.create_user(username="anon", password="97531anonymous13579", email="")
'''

mkdir -p /storage/jobs && mkdir -p /storage/tmp

exec "$@"
