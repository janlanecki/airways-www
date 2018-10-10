"""File containing serializers for models"""
from rest_framework import serializers
from website.models import Captain, Flight


class CaptainSerializer(serializers.ModelSerializer):
    """serializer for the Captain model"""
    class Meta: # pylint: disable=missing-docstring, too-few-public-methods
        model = Captain
        fields = ('id', 'first_name', 'last_name')


class FlightSerializer(serializers.ModelSerializer):
    """serializer for the Flight model"""
    captain = CaptainSerializer()

    class Meta: # pylint: disable=missing-docstring, too-few-public-methods
        model = Flight
        fields = ('id', 'airport_from', 'airport_to', 'day_from', 'day_to', 'time_from', 'time_to',
                  'captain')
        depth = 2

    def update(self, instance, validated_data):
        captain_id = validated_data.pop('captain')
        captain = Captain.objects.get(id=captain_id)
        setattr(instance, 'captain', captain)
        instance.save()

        return instance
