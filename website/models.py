"""Models for the website"""
from django.db import models
from django.conf import settings


class Plane(models.Model):
    """model for airplanes"""
    id = models.CharField(max_length=5, primary_key=True)
    seats = models.PositiveIntegerField()

    def __str__(self):
        return "id: " + str(self.id) + " seats: " + str(self.seats)


class Flight(models.Model):
    """model for flights"""
    airport_from = models.CharField(max_length=150)
    airport_to = models.CharField(max_length=150)
    day_from = models.DateField()
    time_from = models.TimeField()
    day_to = models.DateField()
    time_to = models.TimeField()
    price = models.PositiveIntegerField()
    plane = models.ForeignKey('Plane', null=True, on_delete=models.SET_NULL)
    captain = models.ForeignKey('Captain', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.plane.__str__() + " " + str(self.airport_from) + " " + \
               str(self.day_from) + " " + str(self.airport_to) + " " + str(self.day_to)


class Captain(models.Model):
    """model for captains of flight crews"""
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)

    class Meta: # pylint: disable=missing-docstring, too-few-public-methods
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Ticket(models.Model):
    """model for tickets bought by the specified user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    seats = models.PositiveIntegerField()
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + " " + str(self.first_name) + " " + \
               str(self.last_name) + " seats: " + str(self.seats) + " " + self.flight.__str__()
