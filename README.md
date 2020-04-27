# Room Booking server

This is a server for a room booking web application, built on Django.
Refer to [roombook-ui](https://github.com/wenhongg/roombook-ui) for more reflections on the task. 

## Steps
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


## Deploying to heroku

Setting up Heroku (full steps)
```
	heroku login
	heroku create
	heroku addons:create heroku-postgresql:hobby-dev -a <herokuapp name>
```
Add Procfile ensure django_heroku is set up in settings.py. Use pipreqs to generate requirements.txt (but manually add gunicorn as pipreqs misses that out).
```
	git add .
	git commit
	heroku git:remote -a <herokuapp name>
	git push heroku master
```
Run the following to ensure DB set up properly:
```
	heroku run python manage.py migrate
	heroku run python manage.py migrate --run-syncdb
	heroku run python manage.py loaddata sampledata.json
```
To view real time logs on Heroku, use `heroku logs -t`