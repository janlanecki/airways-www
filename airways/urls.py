"""airlines URL Configuration"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [     # pylint: disable=invalid-name
    path('admin/', admin.site.urls),
    path('', include('website.urls'))
]
