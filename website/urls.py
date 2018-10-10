""" website url configuration
    The `urlpatterns` list routes URLs to views. """

from django.urls import path

from . import views


urlpatterns = [     # pylint: disable=invalid-name
    path('', views.search, name='home'),
    path('search', views.search, name='search'),
    path('details', views.details, name='details'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('api/flights/<day>', views.FlightsAPIList.as_view(), name='list_flights'),
    path('api/flight/<pk>', views.FlightAPIDetails.as_view(), name='flight_details'),
    path('api/get_crews/<id>', views.CrewAPIList.as_view(), name='get_crews'),
    path('api/modify_crew', views.ModifyCrewAPI.as_view(), name='modify_crew'),
    path('api/server_data', views.server_data, name='server_data'),
    path('api/modify_data', views.modify_data, name='modify_data'),
]
