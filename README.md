# Room booking server

This is a server for a room booking web application, produced on Django.

## Steps to deploy
To set up:
```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py loaddata sampledata.json
```
To run server:
```
    python manage.py runserver
```
## Todos

1. Shift more logic to server side
2. Rooms to have more specifications?