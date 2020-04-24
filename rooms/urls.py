from django.urls import path

from . import views

urlpatterns = [
	path('overview', views.overview, name='overview'),
	path('search', views.search, name='search'),
	path('getRoomData', views.getRoomData, name='getRoomData'),
	path('placeBooking', views.placeBooking, name='placeBooking'),
    path('', views.index, name='index')
]