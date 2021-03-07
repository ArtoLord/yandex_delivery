from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.views import Response
from .serializers import CourierSerializer
from .models import Courier, Region
from rest_framework.decorators import api_view


class CourierViewSet(ModelViewSet):
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer

    # TODO remove buisness logic from this
    def create(self, request, *args, **kwargs):
        data = request.data.get('data')
        couriers_to_save = []
        errors = []
        # TODO data validation
        for courier_data in data:
            courier = CourierSerializer(data=courier_data)
            if courier.is_valid():
                couriers_to_save.append(courier)
                continue
            errors.append({'id': courier_data.get('courier_id'), 'errors': {**courier.errors}})

        if errors:
            raise serializers.ValidationError({"validation_error": {"couriers": errors}})
        for courier in couriers_to_save:
            courier.save()

        return Response({"couriers": [{"id": courier.data['courier_id']} for courier in couriers_to_save]}, status=201)
