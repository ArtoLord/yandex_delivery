from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.views import Response
from .serializers import CourierSerializer, UpdateCourierSerializer
from .models import Courier
from django.db import transaction, IntegrityError


class CourierViewSet(ModelViewSet):
    queryset = Courier.objects.all()

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return UpdateCourierSerializer
        return CourierSerializer

    @transaction.atomic()  # Use transactions to avoid partial creation
    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        couriers_to_save = []
        errors = []
        if not data or not isinstance(data, list):
            raise serializers.ValidationError('Data not present or is not a list')
        for courier_data in data:
            courier = CourierSerializer(data=courier_data)
            if courier.is_valid():
                couriers_to_save.append(courier)
                continue
            errors.append({'id': courier_data.get('courier_id'), 'errors': {**courier.errors}})

        if errors:
            raise serializers.ValidationError({"validation_error": {"couriers": errors}})
        for courier in couriers_to_save:
            try:
                courier.save()
            except IntegrityError as err:
                raise serializers.ValidationError({
                    "validation_error": {
                        "couriers": [{
                            'id': courier.data['courier_id'],
                            'errors': [f'Can not create courier instance, may be id is not unique: {err}']
                        }]
                    }
                })

        return Response({"couriers": [{"id": courier.data['courier_id']} for courier in couriers_to_save]}, status=201)
