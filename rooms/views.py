from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import json
import pytz
from . import models as room_models
from datetime import datetime
import pytz

@csrf_exempt
def index(request):
    return HttpResponse("Backend for room booking system.")

#list each room and check each one if booked, and until when
@csrf_exempt
def overview(request):
	#serves SG timezone.
	tz = pytz.timezone('Asia/Singapore') 
	currhour = datetime.now(tz).hour
	
	rooms = room_models.Rooms.objects.all()

	data = []
	for i in rooms:
		c = room_models.Bookings.objects.filter(room_name=i.name,start__lte=currhour,end__gt=currhour)
		print(c)
		if len(c)>0:
			data.append({'roomName': i.name, 'booked': True})
		else:
			data.append({'roomName': i.name, 'booked': False})
	return generateJson(data)

#start time, end time, date, booker,
@csrf_exempt
def placeBooking(request):
	#check validity
	data = json.loads(request.body)
	room_name = data['roomName']
	booker = data['booker']
	contact = data['contact']
	start = data['start']
	end = data['end']
	duration = data['duration']
	date = data['date']

	c = room_models.Bookings.objects.filter(room_name=room_name,date=date,start__lte=start,end__gt=start)
	d = room_models.Bookings.objects.filter(room_name=room_name,date=date,start__lt=end,end__gte=end)

	if len(c)>0 or len(d)>0:
		return generateJson({'response': "An error occured. Someone might have booked this slot right before you."})
	
	#If no conflicts, save data
	en = room_models.Bookings(room_name=room_name,booker=booker,contact=contact,start=start,end=end,duration=duration,date=date)
	en.save()

	successStr = "Success. The room " + room_name + " has been booked." 
	return generateJson({'response': successStr });

#search available slots given date and duration, and also a boolean o
@csrf_exempt
def search(request):
	#check validity
	args = json.loads(request.body)
	#2 arguments
	duration = args['duration']
	date = args['date']

	start = 0
	end = args['duration']
	#if the date is today, bring the start search for time forward.
	if isToday(date):
		print("today was found")
		tz = pytz.timezone('Asia/Singapore') 
		currhour = datetime.now(tz).hour
		start += currhour
		end += currhour

	#full list of rooms
	rooms = room_models.Rooms.objects.all()
	rooms = [i.name for i in rooms]

	#generate data
	data = []
	while end<=24:
		c = room_models.Bookings.objects.filter(date=date,start__lte=start,end__gt=start)
		d = room_models.Bookings.objects.filter(date=date,start__lt=end,end__gte=end)
		unavails = set([i.room_name for i in c] + [i.room_name for i in d])
		avails = [i for i in rooms if i not in unavails]

		for i in avails:
			data.append({'roomName': i, 'start': start, 'end': end})
		start +=1
		end +=1

	return generateJson(data);


#search bookings by room and date
@csrf_exempt
def getRoomData(request):
	args = json.loads(request.body)
	c = room_models.Bookings.objects.filter(room_name=args['room'],date=args['date']).order_by('start')
	data = []
	for i in c:
		duration = i.end - i.start
		if(duration<0):
			duration += 24

		item = {
			"start": i.start,
			"end": i.end, #TODO should i return number 4 or 0400?
			"booker": i.booker,
			"contact": i.contact,
			"duration": duration
		}
		data.append(item)
	return generateJson(data)




### CORE HELPER FUNCTIONS
def isToday(date):
	c = datetime.now().strftime('%d-%m-%Y')
	return date==c

def generateJson(json):
	response = JsonResponse(json, safe=False)
	response['Access-Control-Allow-Origin'] = '*' #very hacky TODO
	return response

