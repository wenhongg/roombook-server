from django.db import models

# Create your models here.


#List of rooms
class Rooms(models.Model):
	name = models.CharField(max_length=20, unique=True)
	size = models.CharField(max_length=3)

class Bookings(models.Model):
	booker = models.CharField(max_length=20)
	contact = models.CharField(max_length=20)
	room_name = models.CharField(max_length=20)
	start = models.IntegerField() #0-23
	end = models.IntegerField() #1-24
	date = models.CharField(max_length=10)
	duration = models.IntegerField()
