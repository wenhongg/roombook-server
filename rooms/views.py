from django.shortcuts import get_object_or_404, render, get_list_or_404, redirect
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
# Create your views here.
import json
import pytz
from . import models as room_models
from datetime import datetime
import pytz
from . import settings
DELETE_PASSWORD = settings.DELETE_PASSWORD

@csrf_exempt
def index(request):
    return HttpResponse("Backend for room booking system.")

#list each room and check each one if booked, and until when
#no arguments required
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
	return generateJson({'data': data})


@csrf_exempt
def deleteBooking(request):
	if not request.body:
		return ErrorResponse("Bad request.")
	args = json.loads(request.body)
	for i in ['roomName','start','date','delete']:
		if i not in args:
			return ErrorResponse("One or more parameters are missing.")
	#check input
	room_name = args['roomName']
	start = args['start']
	date = args['date']

	if(delete!=DELETE_PASSWORD):
		return ErrorResponse("No authorization to delete.")

	c = room_models.Bookings.objects.filter(room_name=room_name,date=date,start=start)
	if(len(c)==0):
		return ErrorResponse("Booking doesn't exist.")

	c.delete()
	return generateJson({'response': 'Successfully deleted.'})

@csrf_exempt
def placeBooking(request):
	#check validity
	if not request.body:
		return ErrorResponse("Bad request.")
	args = json.loads(request.body)
	
	for i in ['roomName','booker','contact','start','end','date']:
		if i not in args:
			return ErrorResponse("One or more parameters are missing.")

	#check input
	room_name = args['roomName']
	booker = args['booker']
	contact = args['contact']
	start = args['start']
	end = args['end']
	date = args['date']

	if not isValidBooker(booker,contact):
		return ErrorResponse("Booker's details were invalid.")
	if not isValidStartEnd(start,end):
		return ErrorResponse("Invalid start and end.")
	if not isValidDate(date):
		return ErrorResponse("Invalid date.")
	if not isValidRoom(room_name):
		return ErrorResponse("Room does not exist.")


	duration = end - start

	c = room_models.Bookings.objects.filter(room_name=room_name,date=date,start__lte=start,end__gt=start)
	d = room_models.Bookings.objects.filter(room_name=room_name,date=date,start__lt=end,end__gte=end)

	#Someone else booked? 200 or 400.
	if len(c)>0 or len(d)>0:
		return generateJson({'response': "An error occured. Someone might have booked this slot right before you."})
	
	#If no conflicts, save data
	en = room_models.Bookings(room_name=room_name,booker=booker,contact=contact,start=start,end=end,duration=duration,date=date)
	en.save()

	successStr = "Success. The room " + room_name + " has been booked." 
	return generateJson({'response': successStr });

#search available slots given date and duration.
@csrf_exempt
def search(request):
	#check validity
	if not request.body:
		return ErrorResponse("Bad request.")
	args = json.loads(request.body)
	for i in ['duration','date']:
		if i not in args:
			print(i + " was missing.")
			return ErrorResponse("One or more parameters are missing.")
	#2 arguments
	duration = args['duration']
	date = args['date']
		
	if not isValidDate(date):
		return ErrorResponse("Invalid date.")
	if not isValidDuration(duration):
		return ErrorResponse("Invalid duration.")

	start = 0
	end = duration

	#if the date is today, bring the start search for time forward.
	if isToday(date):
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

	return generateJson({'data': data});


#search bookings by room and date
@csrf_exempt
def getRoomData(request):
	if not request.body:
		return ErrorResponse("Bad request.")
	args = json.loads(request.body)

	for i in ['room','date']:
		if i not in args:
			print(i + " was missing.")
			return ErrorResponse("One or more parameters are missing.")
	room_name = args['room']
	date = args['date']
	#check if errors exist
	if not isValidDate(date):
		return ErrorResponse("Invalid date.")
	if not isValidRoom(room_name):
		return ErrorResponse("Room does not exist.")

	c = room_models.Bookings.objects.filter(room_name=args['room'],date=args['date']).order_by('start')
	data = []
	for i in c:
		duration = i.end - i.start
		if(duration<0):
			duration += 24

		item = {
			"start": i.start,
			"end": i.end,
			"booker": i.booker,
			"contact": i.contact,
			"duration": duration
		}
		data.append(item)
	return generateJson({'data' : data})




### CORE HELPER FUNCTIONS

#successful return
def generateJson(json):
	json['status'] = 200
	response = JsonResponse(json)

	response['Access-Control-Allow-Origin'] = '*' #very hacky TODO
	return response

def ErrorResponse(messagestring):
	response = JsonResponse({'status': 400, 'message': messagestring})
	response['Access-Control-Allow-Origin'] = '*' #very hacky TODO
	return response


#validation

def isToday(date):
	c = datetime.now().strftime('%d-%m-%Y')
	return date==c

def isValidDate(date):
	if(len(date)!=10):
		return False
	if not date[0:2].isdigit() or not date[3:5].isdigit() or not date[6:10].isdigit():
		return False
	if date[2]!='-' or date[5]!='-':
		return False
	return True

def isValidStartEnd(start,end):
	if type(start)!=int or start>=24 or start<0:
		return False
	if type(end)!=int or end>24 or end<=0:
		return False
	if start>=end:
		return False
	return True

def isValidDuration(duration):
	if type(duration)!=int or duration>24 or duration<=0:
		return False
	return True

def isValidBooker(booker, contact):
	if contact=="" or booker=="":
		return False
	#allow phone number only in contact
	if not contact.isdigit() or len(contact)!=8:
		return False
	return True

def isValidRoom(room_name):
	c = room_models.Rooms.objects.filter(name=room_name)
	if len(c)==0:
		return False
	return True