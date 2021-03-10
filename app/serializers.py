from .models import Courier, Region, Order, Assignation
from rest_framework import serializers
from django.core import validators


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'working_hours', 'regions', 'rating', 'earnings']
        read_only_fields = ['rating', 'earnings']

    working_hours = serializers.ListSerializer(
        allow_empty=True,
        child=serializers.CharField(
            max_length=16,
            validators=(validators.RegexValidator(r'^\d\d:\d\d-\d\d:\d\d$', message="Wrong timerange format"),)
        )
    )

    def to_internal_value(self, data):
        if not data.get('regions'):
            return super(CourierSerializer, self).to_internal_value(data)

        for region_id in data['regions']:
            if not isinstance(region_id, int):
                continue
            Region.objects.get_or_create(region_id=region_id)

        return super(CourierSerializer, self).to_internal_value(data)


class UpdateCourierSerializer(CourierSerializer):
    class Meta:
        model = Courier
        fields = ['courier_id', 'courier_type', 'working_hours', 'regions']
        read_only_fields = ['courier_id']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'weight', 'region', 'delivery_hours']

    delivery_hours = serializers.ListSerializer(
        allow_empty=False,
        child=serializers.CharField(
            max_length=16,
            validators=(validators.RegexValidator(r'^\d\d:\d\d-\d\d:\d\d$', message="Wrong timerange format"),)
        )
    )

    def to_internal_value(self, data):
        region_id = data.get('region')
        if isinstance(region_id, int):
            Region.objects.get_or_create(region_id=region_id)

        return super(OrderSerializer, self).to_internal_value(data)


class OrderIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id']

    id = serializers.IntegerField(source='order_id')


class AssignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignation
        fields = ['orders', 'assign_time']

    orders = OrderIdSerializer(many=True, source="not_completed_orders")
