release: python manage.py migrate --noinput
web: gunicorn --env DJANGO_SETTINGS_MODULE=agencia_app.settings agencia_app.wsgi --bind 0.0.0.0:$PORT --log-file -