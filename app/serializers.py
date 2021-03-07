from .models import Courier, Region
from rest_framework import serializers
from django.db import transaction


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'working_hours', 'regions', 'rating', 'earnings']
        read_only_fields = ['rating', 'earnings']

    working_hours = serializers.ListSerializer(allow_empty=True, child=serializers.CharField(max_length=16))

    def to_internal_value(self, data):
        for region_id in data['regions']:
            if not isinstance(region_id, int):
                continue
            Region.objects.get_or_create(region_id=region_id)

        return super(CourierSerializer, self).to_internal_value(data)

